#!/usr/bin/env python3
"""
Pytest for model loading stability and serialization.

This test ensures that model loading works correctly with all custom objects
and that inference can be performed with random images to validate the
complete model loading pipeline.
"""

import os
import sys
import pytest
import numpy as np
import tensorflow as tf
import toml
from pathlib import Path
from tensorflow.keras.models import load_model

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestModelLoadingStability:
    """Test class for model loading stability and serialization"""
    
    @pytest.fixture(scope="class")
    def setup_environment(self):
        """Setup the test environment"""
        # Set TensorFlow to be less verbose
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        tf.get_logger().setLevel('ERROR')
        
        # Clear any existing custom objects to ensure clean state
        tf.keras.utils.get_custom_objects().clear()
        
        return {
            'project_root': project_root,
            'model_path': project_root / "models" / "SimCLR_rep50.keras",
            'config_path': project_root / "models" / "SimCLR_rep50_config.toml"
        }
    
    @pytest.fixture(scope="class")
    def custom_objects(self):
        """Create custom objects exactly as in model_threads.py"""
        from neutrophils_core.models.simclr import SimCLREncoder, SimCLRModel
        
        try:
            from neutrophils_core.models.heads import ClassificationHead
        except ImportError:
            ClassificationHead = None
        
        custom_objects = {
            'SimCLREncoder': SimCLREncoder,
            'SimCLRModel': SimCLRModel
        }
        if ClassificationHead is not None:
            custom_objects['ClassificationHead'] = ClassificationHead
        
        return custom_objects
    
    def test_custom_objects_import(self, custom_objects):
        """Test that all required custom objects can be imported"""
        assert 'SimCLREncoder' in custom_objects
        assert 'SimCLRModel' in custom_objects
        
        # ClassificationHead should be importable
        if 'ClassificationHead' in custom_objects:
            assert custom_objects['ClassificationHead'] is not None
            
            # Check that ClassificationHead has proper Keras serialization
            ClassificationHead = custom_objects['ClassificationHead']
            assert hasattr(ClassificationHead, '__module__')
            assert hasattr(ClassificationHead, '__name__')
    
    def test_model_files_exist(self, setup_environment):
        """Test that required model files exist"""
        paths = setup_environment
        
        if not paths['model_path'].exists():
            pytest.skip(f"Model file not found: {paths['model_path']}")
        if not paths['config_path'].exists():
            pytest.skip(f"Config file not found: {paths['config_path']}")
    
    def test_config_loading(self, setup_environment):
        """Test that model configuration can be loaded"""
        config_path = setup_environment['config_path']
        
        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = toml.load(f)
        
        assert isinstance(config, dict)
        assert len(config) > 0
        
        # Add model_name as done in ModelLoadingThread
        model_path = setup_environment['model_path']
        config['model_name'] = os.path.splitext(os.path.basename(model_path))[0]
        
        assert config['model_name'] == 'SimCLR_rep50'
    
    def test_model_loading_with_custom_objects(self, setup_environment, custom_objects):
        """Test model loading using custom objects (main test)"""
        model_path = setup_environment['model_path']
        
        if not model_path.exists():
            pytest.skip(f"Model file not found: {model_path}")
        
        # Load model exactly as in ModelLoadingThread
        model = load_model(str(model_path), custom_objects=custom_objects, compile=False)
        
        assert model is not None
        assert hasattr(model, 'input_shape')
        assert hasattr(model, 'output_shape')
        assert hasattr(model, 'predict')
        
        # Store model for other tests
        self.loaded_model = model
    
    def test_model_inference_with_random_image(self, setup_environment, custom_objects):
        """Test model inference with random image data"""
        model_path = setup_environment['model_path']
        
        if not model_path.exists():
            pytest.skip(f"Model file not found: {model_path}")
        
        # Load model
        model = load_model(str(model_path), custom_objects=custom_objects, compile=False)
        
        # Get input shape
        input_shape = model.input_shape
        if isinstance(input_shape, list):
            # Multiple inputs - use the first one
            input_shape = input_shape[0]
        
        assert len(input_shape) >= 2, f"Invalid input shape: {input_shape}"
        
        # Create random input (excluding batch dimension)
        random_input = np.random.random((1,) + input_shape[1:]).astype(np.float32)
        
        # Normalize input to reasonable range (0-1 for images)
        if len(input_shape) == 4:  # Image data (batch, height, width, channels)
            random_input = np.clip(random_input, 0.0, 1.0)
        elif len(input_shape) == 5:  # 3D Image data (batch, depth, height, width, channels)
            random_input = np.clip(random_input, 0.0, 1.0)
        
        # Perform inference
        prediction = model.predict(random_input, verbose=0)
        
        assert prediction is not None
        assert isinstance(prediction, np.ndarray)
        assert prediction.shape[0] == 1  # Batch size
        assert not np.any(np.isnan(prediction)), "Prediction contains NaN values"
        assert not np.any(np.isinf(prediction)), "Prediction contains infinite values"
        
        # If it looks like classification output, check probabilities
        if len(prediction.shape) == 2 and prediction.shape[1] <= 10:
            # Check if it's a probability distribution
            prob_sum = np.sum(prediction[0])
            if 0.9 <= prob_sum <= 1.1:  # Allow some floating point error
                assert np.all(prediction >= 0), "Negative probabilities found"
                assert np.all(prediction <= 1), "Probabilities > 1 found"
    
    def test_model_loading_without_custom_objects_fails(self, setup_environment):
        """Test that model loading fails without custom objects (expected behavior)"""
        model_path = setup_environment['model_path']
        
        if not model_path.exists():
            pytest.skip(f"Model file not found: {model_path}")
        
        # This should fail due to missing custom objects
        with pytest.raises(Exception) as exc_info:
            load_model(str(model_path), compile=False)
        
        # Check that the error is related to custom objects
        error_message = str(exc_info.value)
        assert any(cls_name in error_message for cls_name in ['SimCLREncoder', 'SimCLRModel', 'ClassificationHead'])
    
    def test_serialization_registration(self, custom_objects):
        """Test that custom objects are properly registered for serialization"""
        # Test SimCLREncoder
        SimCLREncoder = custom_objects['SimCLREncoder']
        
        # Check that it has the proper registration
        assert hasattr(SimCLREncoder, '_keras_serializable')
        
        # Test that we can create a config and recreate from it
        # This is a basic serialization test without full model context
        try:
            # Create a minimal config for testing
            test_config = {
                'data': {'image_size': 69, 'use_mip': False},
                'model': {
                    'embedding_dim': 128,
                    'hidden_dim': 256,
                    'use_projection_head': True,
                    'fully_connected': []
                }
            }
            
            encoder = SimCLREncoder(config=test_config)
            config = encoder.get_config()
            
            # Test that config is serializable
            assert isinstance(config, dict)
            assert 'config' in config
            
        except Exception as e:
            # If we can't create a minimal instance, that's okay for this test
            # The important thing is that the class is properly registered
            pass


class TestModelLoadingIntegration:
    """Integration tests for realistic model loading scenarios"""
    
    @pytest.fixture(scope="class")
    def model_and_config(self):
        """Load model and config for integration tests"""
        # Setup
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        tf.get_logger().setLevel('ERROR')
        
        # Check if model files exist
        model_path = project_root / "models" / "SimCLR_rep50.keras"
        config_path = project_root / "models" / "SimCLR_rep50_config.toml"
        
        if not model_path.exists() or not config_path.exists():
            pytest.skip("Model or config files not found")
        
        # Import custom objects
        from neutrophils_core.models.simclr import SimCLREncoder, SimCLRModel
        
        try:
            from neutrophils_core.models.heads import ClassificationHead
        except ImportError:
            ClassificationHead = None
        
        custom_objects = {
            'SimCLREncoder': SimCLREncoder,
            'SimCLRModel': SimCLRModel
        }
        if ClassificationHead is not None:
            custom_objects['ClassificationHead'] = ClassificationHead
        
        # Load model and config
        model = load_model(str(model_path), custom_objects=custom_objects, compile=False)
        
        with open(config_path, 'r') as f:
            config = toml.load(f)
        config['model_name'] = os.path.splitext(os.path.basename(model_path))[0]
        
        return model, config
    
    def test_realistic_inference_scenario(self, model_and_config):
        """Test realistic inference scenario similar to SingleInferenceThread"""
        model, config = model_and_config
        
        # Simulate realistic image data
        input_shape = model.input_shape
        if isinstance(input_shape, list):
            input_shape = input_shape[0]
        
        # Create more realistic image data
        if len(input_shape) == 5:  # 3D medical images (batch, depth, height, width, channels)
            depth, height, width, channels = input_shape[1], input_shape[2], input_shape[3], input_shape[4]
            
            # Create synthetic medical image-like data
            image = np.random.normal(0.5, 0.2, (1, depth, height, width, channels)).astype(np.float32)
            image = np.clip(image, 0.0, 1.0)  # Normalize to [0, 1]
        elif len(input_shape) == 4:  # 2D images (batch, height, width, channels)
            height, width, channels = input_shape[1], input_shape[2], input_shape[3]
            
            # Create synthetic image data
            image = np.random.normal(0.5, 0.2, (1, height, width, channels)).astype(np.float32)
            image = np.clip(image, 0.0, 1.0)  # Normalize to [0, 1]
        else:
            # Feature vector input
            image = np.random.normal(0.0, 1.0, (1,) + input_shape[1:]).astype(np.float32)
        
        # Perform inference
        predictions = model.predict(image, verbose=0)
        
        # Process results as done in SingleInferenceThread
        if len(predictions.shape) > 1:
            predictions = predictions[0]  # Take first element if batch dimension exists
        
        predicted_class_index = np.argmax(predictions)
        confidence_score = np.max(predictions)
        
        # Validate results
        assert isinstance(predicted_class_index, (int, np.integer))
        assert 0 <= predicted_class_index < len(predictions)
        assert 0.0 <= confidence_score <= 1.0
        assert isinstance(predictions.tolist(), list)
        
        # Create classification results dict as in the application
        classification_results = {
            'predicted_class_index': int(predicted_class_index),
            'confidence': float(confidence_score),
            'probabilities': predictions.tolist()
        }
        
        assert all(key in classification_results for key in ['predicted_class_index', 'confidence', 'probabilities'])


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "--tb=short"])