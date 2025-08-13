#!/usr/bin/env python3
"""
Comprehensive Test Suite for Replicate Batch Process
DO NOT DELETE - Run before every commit
Tests all models to ensure nothing is broken
"""

import os
import sys
import time
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from replicate_batch_process.main import (
    replicate_model_calling,
    get_supported_parameters,
    supports_reference_image,
    supports_reference_audio,
    REPLICATE_MODELS
)

# Test configuration
TEST_CONFIG = {
    'run_expensive_tests': False,  # Set to True to test video models
    'test_output_dir': 'output/comprehensive_test',
    'max_retries': 2,
    'timeout_seconds': 120,
    'test_resources_dir': '/Users/lgg/coding/vibe_coding/test_resource_files'
}

class ComprehensiveTestSuite:
    """Comprehensive test suite for all models"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Create test output directory
        os.makedirs(TEST_CONFIG['test_output_dir'], exist_ok=True)
        
        # Check API token
        if not os.getenv("REPLICATE_API_TOKEN"):
            raise ValueError("❌ REPLICATE_API_TOKEN not found in environment")
        
        # Load test resources
        self.test_resources = self._load_test_resources()
    
    def _load_test_resources(self):
        """Load available test resources from test_resource_files directory"""
        resources = {
            'images': [],
            'audio': [],
            'text': [],
            'video': [],
            'json': [],
            'system_prompts': {},
            'story_scenes': []  # Add story scenes
        }
        
        test_dir = TEST_CONFIG['test_resources_dir']
        if not os.path.exists(test_dir):
            print(f"⚠️ Test resources directory not found: {test_dir}")
            return resources
        
        # Load image files (scene_01.png to scene_55.png)
        image_dir = os.path.join(test_dir, 'images')
        if os.path.exists(image_dir):
            resources['images'] = [
                os.path.join(image_dir, f) for f in os.listdir(image_dir)
                if f.endswith(('.png', '.jpg', '.jpeg'))
            ]
            # Sort to get scene files in order
            resources['images'].sort()
        
        # Load audio files (scene_01.mp3 to scene_55.mp3 and SRT files)
        audio_dir = os.path.join(test_dir, 'audio')
        if os.path.exists(audio_dir):
            mp3_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith('.mp3')]
            srt_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith('.srt')]
            resources['audio'] = sorted(mp3_files)
            resources['srt'] = sorted(srt_files)
        
        # Load video clips (with srt overlays)
        video_dir = os.path.join(test_dir, 'video_clips')
        if os.path.exists(video_dir):
            resources['video'] = [
                os.path.join(video_dir, f) for f in os.listdir(video_dir)
                if f.endswith(('.mp4', '.mov'))
            ]
        
        # Load text prompts from test_prompts.txt
        text_file = os.path.join(test_dir, 'text', 'test_prompts.txt')
        if os.path.exists(text_file):
            with open(text_file, 'r') as f:
                content = f.read()
                # Extract prompts from the file
                for line in content.split('\n'):
                    if line.strip() and not line.startswith('#') and '. ' in line:
                        prompt = line.split('. ', 1)[1] if '. ' in line else line
                        resources['text'].append(prompt.strip())
        
        # Load JSON files (image_descriptions.json and structured_design.json)
        json_files = [f for f in os.listdir(test_dir) if f.endswith('.json')]
        for json_file in json_files:
            full_path = os.path.join(test_dir, json_file)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    resources['json'].append({
                        'name': json_file,
                        'path': full_path,
                        'data': data
                    })
                    
                    # Load story scenes from structured_design.json
                    if 'scene_list' in data:
                        resources['story_scenes'] = data['scene_list']
                        resources['cover_image_description'] = data.get('cover_image_description', '')
                        resources['story_title'] = data.get('story_title', '')
                        resources['illustration_style'] = data.get('illustration_style', '')
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                pass
        
        # Load system prompts
        system_prompt_files = [f for f in os.listdir(test_dir) if f.startswith('system_prompt_')]
        for prompt_file in system_prompt_files:
            prompt_type = prompt_file.replace('system_prompt_', '').replace('.txt', '')
            with open(os.path.join(test_dir, prompt_file), 'r') as f:
                resources['system_prompts'][prompt_type] = f.read()
        
        print(f"📚 Loaded test resources from {test_dir}:")
        print(f"   - {len(resources['images'])} scene images")
        print(f"   - {len(resources['audio'])} audio files (MP3)")
        print(f"   - {len(resources.get('srt', []))} subtitle files (SRT)")
        print(f"   - {len(resources['video'])} video clips")
        print(f"   - {len(resources['text'])} text prompts")
        print(f"   - {len(resources['json'])} JSON files")
        print(f"   - {len(resources['system_prompts'])} system prompts")
        print(f"   - {len(resources['story_scenes'])} story scenes")
        if resources['story_title']:
            print(f"   - Story: {resources['story_title']}")
        
        return resources
    
    def test_image_models(self):
        """Test all image generation models"""
        print("\n" + "=" * 60)
        print("🖼️  TESTING IMAGE MODELS")
        print("=" * 60)
        
        # First, generate character images for testing
        character_images = []
        prompts = []
        
        # Get character descriptions from JSON
        if 'character_list' in self.test_resources.get('json', [{}])[0].get('data', {}):
            characters = self.test_resources['json'][0]['data']['character_list']
            style = self.test_resources.get('illustration_style', '')
            
            # Use first 3 characters for testing
            for i, char in enumerate(characters[:3]):
                char_desc = char.get('character_image_description', '')
                char_name = char.get('character_name', '')
                
                # Add illustration style to character description
                if style and not char_desc.startswith(style):
                    full_prompt = f"{style}. {char_desc}"
                else:
                    full_prompt = char_desc
                
                prompts.append(full_prompt)
                print(f"   Character {i+1}: {char_name}")
                
                # Store expected output path for later use as reference
                character_images.append(f"{TEST_CONFIG['test_output_dir']}/char_{char_name}.jpg")
        else:
            # Fallback to scene descriptions if no characters
            if self.test_resources['story_scenes']:
                # Randomly select 3 scenes for testing
                import random
                selected_scenes = random.sample(self.test_resources['story_scenes'], 
                                              min(3, len(self.test_resources['story_scenes'])))
                for scene in selected_scenes:
                    # Add illustration style to the prompt
                    style = self.test_resources.get('illustration_style', '')
                    scene_desc = scene.get('scene_image_description', '')
                    if style and not scene_desc.startswith(style):
                        full_prompt = f"{style}. {scene_desc}"
                    else:
                        full_prompt = scene_desc
                    prompts.append(full_prompt)
                    print(f"   Scene {scene['scene_number']}: {scene['scene_name']}")
            else:
                # Final fallback
                prompts = [
                    'A simple test image with the text "TEST" clearly visible',
                    'A small red cube on white background',
                    'A minimalist logo design'
                ]
        
        # Select a reference image if available (use test_reference.jpg or first scene image)
        reference_image = None
        if self.test_resources['images']:
            # Look for test_reference.jpg or test_gradient.jpg first
            for img in self.test_resources['images']:
                if 'test_reference' in img or 'test_gradient' in img:
                    reference_image = img
                    break
            # Fallback to first scene image
            if not reference_image:
                reference_image = self.test_resources['images'][0]
        
        # Create tests for character generation
        image_tests = []
        for i, (prompt, char_img_path) in enumerate(zip(prompts[:3], character_images[:3])):
            models = ['qwen/qwen-image', 'black-forest-labs/flux-dev', 'google/imagen-4-ultra']
            if i < len(models):
                params = {}
                if models[i] == 'qwen/qwen-image':
                    params = {'output_format': 'jpg', 'guidance': 4}
                elif models[i] == 'black-forest-labs/flux-dev':
                    params = {'go_fast': True, 'num_inference_steps': 10}
                elif models[i] == 'google/imagen-4-ultra':
                    params = {'output_format': 'jpg'}
                
                image_tests.append({
                    'model': models[i],
                    'prompt': prompt,
                    'params': params,
                    'output_file': char_img_path if character_images else None
                })
        
        # Store paths of generated character images for flux-kontext-max test
        self.generated_character_images = []
        
        for test in image_tests:
            model = test['model']
            if model not in REPLICATE_MODELS:
                self.results[model] = "⏭️ SKIPPED: Not configured"
                print(f"⏭️ {model}: Not in configuration")
                continue
            
            try:
                # Use specified output file if available (for character images)
                output_file = test.get('output_file') or f"{TEST_CONFIG['test_output_dir']}/{model.replace('/', '_')}.jpg"
                result = replicate_model_calling(
                    prompt=test['prompt'],
                    model_name=model,
                    output_filepath=output_file,
                    **test.get('params', {})
                )
                
                # Verify file exists
                if os.path.exists(result[0]):
                    file_size = os.path.getsize(result[0])
                    if file_size > 0:
                        self.results[model] = f"✅ PASS (size: {file_size} bytes)"
                        print(f"✅ {model}: Success ({file_size} bytes)")
                        # Save character image path for later use
                        self.generated_character_images.append(result[0])
                    else:
                        self.results[model] = "❌ FAIL: Empty file"
                        print(f"❌ {model}: Empty file generated")
                else:
                    self.results[model] = "❌ FAIL: File not created"
                    print(f"❌ {model}: File not created")
                    
            except Exception as e:
                self.results[model] = f"❌ FAIL: {str(e)[:100]}"
                print(f"❌ {model}: {str(e)[:100]}")
        
        # Now test flux-kontext-max with generated character image as input_image
        if self.generated_character_images and 'black-forest-labs/flux-kontext-max' in REPLICATE_MODELS:
            print("\n🎨 Testing flux-kontext-max with character reference image")
            
            # Use first generated character image as reference
            input_image = self.generated_character_images[0]
            print(f"   Using character image: {input_image}")
            
            # Get a scene that features the same character
            kontext_prompt = "Enhance this character in a new scene"
            if self.test_resources['story_scenes']:
                # Find a scene with a character
                for scene in self.test_resources['story_scenes'][:10]:  # Check first 10 scenes
                    if scene.get('scene_major_character'):
                        char_name = scene['scene_major_character']
                        scene_desc = scene.get('scene_image_description', '')
                        style = self.test_resources.get('illustration_style', '')
                        
                        # Create prompt with scene description
                        if style and not scene_desc.startswith(style):
                            kontext_prompt = f"{style}. {scene_desc}"
                        else:
                            kontext_prompt = scene_desc
                        
                        print(f"   Scene {scene['scene_number']}: {scene['scene_name']} (featuring {char_name})")
                        break
            
            try:
                output_file = f"{TEST_CONFIG['test_output_dir']}/flux_kontext_max_with_char.jpg"
                result = replicate_model_calling(
                    prompt=kontext_prompt,
                    model_name='black-forest-labs/flux-kontext-max',
                    output_filepath=output_file,
                    input_image=input_image,  # Use input_image, not reference_image!
                    aspect_ratio='16:9',
                    output_format='jpg'
                )
                
                # Verify file exists
                if os.path.exists(result[0]):
                    file_size = os.path.getsize(result[0])
                    if file_size > 0:
                        self.results['black-forest-labs/flux-kontext-max'] = f"✅ PASS (size: {file_size} bytes)"
                        print(f"✅ flux-kontext-max: Success with character reference ({file_size} bytes)")
                    else:
                        self.results['black-forest-labs/flux-kontext-max'] = "❌ FAIL: Empty file"
                        print(f"❌ flux-kontext-max: Empty file generated")
                else:
                    self.results['black-forest-labs/flux-kontext-max'] = "❌ FAIL: File not created"
                    print(f"❌ flux-kontext-max: File not created")
                    
            except Exception as e:
                self.results['black-forest-labs/flux-kontext-max'] = f"❌ FAIL: {str(e)[:100]}"
                print(f"❌ flux-kontext-max: {str(e)[:100]}")
    
    def test_audio_models(self):
        """Test all audio generation models"""
        print("\n" + "=" * 60)
        print("🎤 TESTING AUDIO MODELS")
        print("=" * 60)
        
        # Use audio prompts from test resources
        audio_prompts = []
        if self.test_resources['text']:
            # Extract audio/TTS specific prompts
            for prompt in self.test_resources['text']:
                if any(word in prompt.lower() for word in ['hello', 'test', 'audio', 'speak']):
                    audio_prompts.append(prompt)
        
        if not audio_prompts:
            audio_prompts = ['Testing audio generation. One, two, three.']
        
        # Select reference audio if available
        reference_audio = None
        if self.test_resources['audio']:
            # Prefer MP3 files for voice cloning
            mp3_files = [f for f in self.test_resources['audio'] if f.endswith('.mp3')]
            reference_audio = mp3_files[0] if mp3_files else self.test_resources['audio'][0]
        
        audio_tests = [
            {
                'model': 'resemble-ai/chatterbox',
                'prompt': audio_prompts[0],
                'params': {
                    'temperature': 0.8, 
                    'seed': 42,
                    'audio_prompt': reference_audio  # Add reference audio if available
                } if reference_audio else {
                    'temperature': 0.8,
                    'seed': 42
                }
            }
        ]
        
        # Add test with different emotions if we have multiple prompts
        if len(audio_prompts) > 1:
            audio_tests.append({
                'model': 'resemble-ai/chatterbox',
                'prompt': audio_prompts[1],
                'params': {
                    'temperature': 1.0,
                    'exaggeration': 1.5,  # More expressive
                    'cfg_weight': 0.8     # Higher pace
                }
            })
        
        for test in audio_tests:
            model = test['model']
            if model not in REPLICATE_MODELS:
                self.results[model] = "⏭️ SKIPPED: Not configured"
                print(f"⏭️ {model}: Not in configuration")
                continue
            
            try:
                output_file = f"{TEST_CONFIG['test_output_dir']}/{model.replace('/', '_')}.wav"
                result = replicate_model_calling(
                    prompt=test['prompt'],
                    model_name=model,
                    output_filepath=output_file,
                    **test.get('params', {})
                )
                
                # Verify file exists
                if os.path.exists(result[0]):
                    file_size = os.path.getsize(result[0])
                    if file_size > 0:
                        self.results[model] = f"✅ PASS (size: {file_size} bytes)"
                        print(f"✅ {model}: Success ({file_size} bytes)")
                    else:
                        self.results[model] = "❌ FAIL: Empty file"
                        print(f"❌ {model}: Empty file generated")
                else:
                    self.results[model] = "❌ FAIL: File not created"
                    print(f"❌ {model}: File not created")
                    
            except Exception as e:
                self.results[model] = f"❌ FAIL: {str(e)[:100]}"
                print(f"❌ {model}: {str(e)[:100]}")
    
    def test_batch_processing(self):
        """Test batch processing capabilities"""
        print("\n" + "=" * 60)
        print("🔄 TESTING BATCH PROCESSING")
        print("=" * 60)
        
        # Import batch processor
        try:
            from replicate_batch_process.intelligent_batch_processor import IntelligentBatchProcessor, BatchRequest
        except ImportError:
            print("❌ Could not import batch processor")
            self.results['batch_processing'] = "❌ FAIL: Import error"
            return
        
        # Use real scene descriptions from story JSON
        if not self.test_resources['story_scenes']:
            print("⚠️ No story scenes available, using default prompts")
            scene_prompts = [
                "A red cube on white background",
                "A blue sphere on black background", 
                "A green pyramid on gray background"
            ]
        else:
            # Get illustration style if available
            style = self.test_resources.get('illustration_style', '')
            
            # Select different scenes for batch testing
            import random
            scenes = self.test_resources['story_scenes']
            
            # For reproducible tests, use specific scene indices
            test_scene_indices = [0, len(scenes)//2, len(scenes)-1]  # First, middle, last
            scene_prompts = []
            
            for idx in test_scene_indices:
                if idx < len(scenes):
                    scene = scenes[idx]
                    scene_desc = scene.get('scene_image_description', '')
                    # Add illustration style if available
                    if style and not scene_desc.startswith(style):
                        full_prompt = f"{style}. {scene_desc}"
                    else:
                        full_prompt = scene_desc
                    scene_prompts.append(full_prompt)
                    print(f"   Using Scene {scene['scene_number']}: {scene['scene_name']}")
            
            # Ensure we have at least 3 prompts
            while len(scene_prompts) < 3:
                random_scene = random.choice(scenes)
                scene_desc = random_scene.get('scene_image_description', '')
                if style and not scene_desc.startswith(style):
                    full_prompt = f"{style}. {scene_desc}"
                else:
                    full_prompt = scene_desc
                scene_prompts.append(full_prompt)
        
        # Test 1: Linear/Sequential test - single call for each model (3 images total)
        print("\n📝 Test 1: Linear/Sequential test - one scene per model")
        
        models_to_test = ["qwen/qwen-image", "black-forest-labs/flux-dev", "google/imagen-4-ultra"]
        linear_results = []
        
        for i, model in enumerate(models_to_test):
            if i < len(scene_prompts):
                prompt = scene_prompts[i]
                print(f"   Testing {model} with scene {i+1}...")
                
                try:
                    # Single request for this model
                    request = BatchRequest(
                        prompt=prompt,
                        model_name=model,
                        output_filepath=f"{TEST_CONFIG['test_output_dir']}/linear_{model.replace('/', '_')}_{i+1}.jpg"
                    )
                    
                    # Process single request (not batch)
                    batch_processor = IntelligentBatchProcessor(max_concurrent=1)
                    
                    # Handle event loop properly
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    results = loop.run_until_complete(batch_processor.process_intelligent_batch([request]))
                    
                    if results and results[0].success:
                        linear_results.append("✅")
                        print(f"      ✅ {model}: Success")
                    else:
                        linear_results.append("❌")
                        print(f"      ❌ {model}: Failed")
                        
                except Exception as e:
                    linear_results.append("❌")
                    print(f"      ❌ {model}: {str(e)[:50]}")
        
        success_count = linear_results.count("✅")
        self.results['test1_linear'] = f"{'✅ PASS' if success_count == len(models_to_test) else '⚠️ PARTIAL'} ({success_count}/{len(models_to_test)})"
        print(f"   Linear test complete: {success_count}/{len(models_to_test)} models succeeded")
        
        # Test 2: Batch processing - 3 scenes × 3 models = 9 images
        print("\n📝 Test 2: Batch processing - 3 scenes × 3 models = 9 images")
        
        # Get 3 different scenes for batch testing
        batch_scene_prompts = []
        if len(self.test_resources['story_scenes']) >= 3:
            scenes = self.test_resources['story_scenes']
            style = self.test_resources.get('illustration_style', '')
            
            # Select 3 different scenes
            scene_indices = [5, 25, 45] if len(scenes) >= 46 else [0, len(scenes)//2, len(scenes)-1]
            
            for idx in scene_indices:
                if idx < len(scenes):
                    scene = scenes[idx]
                    scene_desc = scene.get('scene_image_description', '')
                    if style and not scene_desc.startswith(style):
                        full_prompt = f"{style}. {scene_desc}"
                    else:
                        full_prompt = scene_desc
                    batch_scene_prompts.append(full_prompt)
                    print(f"   Using Scene {scene['scene_number']}: {scene['scene_name']}")
        else:
            batch_scene_prompts = scene_prompts  # Reuse if not enough scenes
        
        # Process each model with all 3 scenes (batch)
        models = ["qwen/qwen-image", "black-forest-labs/flux-dev", "google/imagen-4-ultra"]
        total_batch_success = 0
        total_batch_requests = 0
        
        for model_idx, model in enumerate(models):
            print(f"\n   Batch processing {model} with 3 scenes...")
            
            # Create batch requests for this model
            model_requests = []
            for scene_idx, prompt in enumerate(batch_scene_prompts):
                model_requests.append(
                    BatchRequest(
                        prompt=prompt,
                        model_name=model,
                        output_filepath=f"{TEST_CONFIG['test_output_dir']}/batch_m{model_idx+1}_s{scene_idx+1}.jpg"
                    )
                )
            
            try:
                batch_processor = IntelligentBatchProcessor(max_concurrent=3)
                
                # Handle event loop properly
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(batch_processor.process_intelligent_batch(model_requests))
                
                success_count = sum(1 for r in results if r.success)
                total_batch_success += success_count
                total_batch_requests += len(model_requests)
                
                print(f"      {model}: {success_count}/{len(model_requests)} succeeded")
                
            except Exception as e:
                print(f"      ❌ {model} batch failed: {str(e)[:50]}")
                total_batch_requests += len(model_requests)
        
        self.results['test2_batch'] = f"✅ PASS ({total_batch_success}/{total_batch_requests})"
        print(f"   Batch test complete: {total_batch_success}/{total_batch_requests} images generated")
        
        # Test 3: Mixed batch - parallel processing with fallback (3 images)
        print("\n📝 Test 3: Mixed batch - parallel processing with fallback")
        
        # Create mixed requests: 3 different models, 3 different scenes, processed in parallel
        mixed_requests = []
        models = ["qwen/qwen-image", "black-forest-labs/flux-dev", "google/imagen-4-ultra"]
        
        # Use first 3 scenes for mixed batch
        for i, model in enumerate(models):
            if i < len(scene_prompts):
                mixed_requests.append(
                    BatchRequest(
                        prompt=scene_prompts[i],
                        model_name=model,
                        output_filepath=f"{TEST_CONFIG['test_output_dir']}/mixed_{model.replace('/', '_')}.jpg"
                    )
                )
                print(f"   Queuing {model} with scene {i+1}")
        
        try:
            print(f"\n   Processing {len(mixed_requests)} requests in parallel with fallback...")
            batch_processor = IntelligentBatchProcessor(max_concurrent=3)
            
            # Handle event loop properly
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            results = loop.run_until_complete(batch_processor.process_intelligent_batch(mixed_requests))
            
            success_count = sum(1 for r in results if r.success)
            print(f"   ✅ Mixed batch: {success_count}/{len(mixed_requests)} succeeded")
            
            # Show results
            for result in results:
                status = "✅" if result.success else "❌"
                print(f"      {status} {result.model_name}: {'Success' if result.success else result.error[:30]}")
            
            self.results['test3_mixed'] = f"✅ PASS ({success_count}/{len(mixed_requests)})"
            
        except Exception as e:
            print(f"   ❌ Mixed batch failed: {str(e)[:100]}")
            self.results['test3_mixed'] = f"❌ FAIL: {str(e)[:50]}"
    
    def test_video_models(self):
        """Test video generation models (expensive, optional)"""
        print("\n" + "=" * 60)
        print("🎬 TESTING VIDEO MODELS")
        print("=" * 60)
        
        if not TEST_CONFIG['run_expensive_tests']:
            print("⚠️ Skipping video models (expensive). Set run_expensive_tests=True to enable")
            self.results['video_models'] = "⏭️ SKIPPED: Expensive tests disabled"
            return
        
        video_tests = [
            {
                'model': 'google/veo-3-fast',
                'prompt': 'A spinning cube, 3 seconds',
                'params': {'resolution': '720p'}
            }
        ]
        
        for test in video_tests:
            model = test['model']
            if model not in REPLICATE_MODELS:
                self.results[model] = "⏭️ SKIPPED: Not configured"
                continue
            
            try:
                output_file = f"{TEST_CONFIG['test_output_dir']}/{model.replace('/', '_')}.mp4"
                result = replicate_model_calling(
                    prompt=test['prompt'],
                    model_name=model,
                    output_filepath=output_file,
                    **test.get('params', {})
                )
                self.results[model] = "✅ PASS"
                print(f"✅ {model}: Success")
            except Exception as e:
                self.results[model] = f"❌ FAIL: {str(e)[:100]}"
                print(f"❌ {model}: {str(e)[:100]}")
    
    def test_reference_support(self):
        """Test reference file support functions"""
        print("\n" + "=" * 60)
        print("🔍 TESTING REFERENCE SUPPORT")
        print("=" * 60)
        
        # Test image reference support
        image_ref_models = ['black-forest-labs/flux-kontext-max', 'google/veo-3-fast']
        for model in image_ref_models:
            if model in REPLICATE_MODELS:
                has_ref = supports_reference_image(model)
                expected = REPLICATE_MODELS[model].get('reference_image', False)
                if has_ref == expected:
                    print(f"✅ {model}: Reference image support = {has_ref}")
                    self.results[f"{model}_ref_image"] = "✅ PASS"
                else:
                    print(f"❌ {model}: Reference image mismatch")
                    self.results[f"{model}_ref_image"] = "❌ FAIL"
        
        # Test audio reference support
        audio_ref_models = ['resemble-ai/chatterbox']
        for model in audio_ref_models:
            if model in REPLICATE_MODELS:
                has_ref = supports_reference_audio(model)
                expected = REPLICATE_MODELS[model].get('reference_audio', False)
                if has_ref == expected:
                    print(f"✅ {model}: Reference audio support = {has_ref}")
                    self.results[f"{model}_ref_audio"] = "✅ PASS"
                else:
                    print(f"❌ {model}: Reference audio mismatch")
                    self.results[f"{model}_ref_audio"] = "❌ FAIL"
        
        # Report on available test resources for reference testing
        if self.test_resources['images']:
            print(f"📸 Available reference images: {len(self.test_resources['images'])} scene images")
        if self.test_resources['audio']:
            print(f"🎵 Available reference audio: {len(self.test_resources['audio'])} MP3 files")
        if self.test_resources.get('srt'):
            print(f"📝 Available SRT files: {len(self.test_resources['srt'])} subtitle files")
    
    def test_parameter_functions(self):
        """Test parameter retrieval functions"""
        print("\n" + "=" * 60)
        print("⚙️ TESTING PARAMETER FUNCTIONS")
        print("=" * 60)
        
        for model in list(REPLICATE_MODELS.keys())[:3]:  # Test first 3 models
            try:
                params = get_supported_parameters(model, format_for_display=False)
                if isinstance(params, dict) and 'model_name' in params:
                    print(f"✅ {model}: Parameters retrieved successfully")
                    self.results[f"{model}_params"] = "✅ PASS"
                else:
                    print(f"❌ {model}: Invalid parameter format")
                    self.results[f"{model}_params"] = "❌ FAIL"
            except Exception as e:
                print(f"❌ {model}: Parameter retrieval failed - {e}")
                self.results[f"{model}_params"] = f"❌ FAIL: {str(e)[:50]}"
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Count results
        passed = sum(1 for r in self.results.values() if "✅ PASS" in str(r))
        failed = sum(1 for r in self.results.values() if "❌ FAIL" in str(r))
        skipped = sum(1 for r in self.results.values() if "⏭️ SKIP" in str(r))
        total = len(self.results)
        
        # Display results
        print("\n📋 Detailed Results:")
        print("-" * 70)
        for test, result in self.results.items():
            status_emoji = "✅" if "PASS" in result else "❌" if "FAIL" in result else "⏭️"
            print(f"{status_emoji} {test}: {result}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📈 Summary:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏭️ Skipped: {skipped}")
        print(f"   Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        # Duration
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print(f"   Duration: {duration:.2f} seconds")
        
        # Save report to file
        report_file = f"{TEST_CONFIG['test_output_dir']}/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results,
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'skipped': skipped,
                    'success_rate': f"{(passed/total*100):.1f}%" if total > 0 else "N/A"
                }
            }, f, indent=2)
        print(f"\n📄 Report saved to: {report_file}")
        
        # Final verdict
        print("\n" + "=" * 70)
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Safe to commit and deploy.")
            return True
        else:
            print("❌ SOME TESTS FAILED! Please fix issues before committing.")
            print("   Run individual tests to debug failures.")
            return False
    
    def run(self):
        """Run all tests"""
        self.start_time = time.time()
        
        print("\n" + "=" * 70)
        print("🚀 STARTING COMPREHENSIVE TEST SUITE")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Output Directory: {TEST_CONFIG['test_output_dir']}")
        print("=" * 70)
        
        # Run test categories
        self.test_parameter_functions()
        self.test_reference_support()
        self.test_image_models()
        self.test_audio_models()
        self.test_batch_processing()  # New batch processing tests
        self.test_video_models()
        
        self.end_time = time.time()
        
        # Generate report
        return self.generate_report()

def main():
    """Main entry point"""
    try:
        # Create and run test suite
        suite = ComprehensiveTestSuite()
        success = suite.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()