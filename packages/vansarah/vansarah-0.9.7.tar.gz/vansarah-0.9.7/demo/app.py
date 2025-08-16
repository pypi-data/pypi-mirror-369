import spaces
from vansarah import KModel, KPipeline
import gradio as gr
import torch
import numpy as np
import wave
import io
import time
import re
import json
from typing import List, Tuple, Optional, Dict
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range, low_pass_filter, high_pass_filter
import os
import random

# Khởi tạo môi trường - Ưu tiên GPU
CUDA_AVAILABLE = torch.cuda.is_available()

class TTSModel:
    def __init__(self):
        self.use_cuda = CUDA_AVAILABLE
        self.models = {}
        
        try:
            if self.use_cuda:
                self.models['cuda'] = torch.compile(KModel().to('cuda').eval(), mode='max-autotune')
                with torch.no_grad():
                    _ = self.models['cuda'](torch.randn(1, 64).cuda(), torch.randn(1, 80, 100).cuda(), 1.0)
            
            self.models['cpu'] = KModel().to('cpu').eval()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.models = {'cpu': KModel().to('cpu').eval()}
        
        self.pipelines = {
            'a': KPipeline(lang_code='a', model=False),
            'b': KPipeline(lang_code='b', model=False)
        }
        
        self.voice_cache = {}

model_manager = TTSModel()

VOICES = {
    # 🇺🇸 Giọng nữ Mỹ (American English - Female)
    '🇺🇸 🙎 Heart ❤️': 'af_heart',
    '🇺🇸 🙎 Bella 🔥': 'af_bella',
    '🇺🇸 🙎 Nicole 🎧': 'af_nicole',
    '🇺🇸 🙎 Aoede': 'af_aoede',
    '🇺🇸 🙎 Kore': 'af_kore',
    '🇺🇸 🙎 Sarah': 'af_sarah',
    '🇺🇸 🙎 Nova': 'af_nova',
    '🇺🇸 🙎 Sky': 'af_sky',
    '🇺🇸 🙎 Alloy': 'af_alloy',
    '🇺🇸 🙎 Jessica': 'af_jessica',
    '🇺🇸 🙎 River': 'af_river',
    
    # 🇺🇸 Giọng nam Mỹ (American English - Male)
    '🇺🇸 🤵 Michael': 'am_michael',
    '🇺🇸 🤵 Fenrir': 'am_fenrir',
    '🇺🇸 🤵 Puck': 'am_puck',
    '🇺🇸 🤵 Echo': 'am_echo',
    '🇺🇸 🤵 Eric': 'am_eric',
    '🇺🇸 🤵 Liam': 'am_liam',
    '🇺🇸 🤵 Onyx': 'am_onyx',
    '🇺🇸 🤵 Santa': 'am_santa',
    '🇺🇸 🤵 Adam': 'am_adam',
    
    # 🇬🇧 Giọng nữ Anh (British English - Female)
    '🇬🇧 🙎 Emma': 'bf_emma',
    '🇬🇧 🙎 Isabella': 'bf_isabella',
    '🇬🇧 🙎 Alice': 'bf_alice',
    '🇬🇧 🙎 Lily': 'bf_lily',
    
    # 🇬🇧 Giọng nam Anh (British English - Male)
    '🇬🇧 🤵 George': 'bm_george',
    '🇬🇧 🤵 Fable': 'bm_fable',
    '🇬🇧 🤵 Lewis': 'bm_lewis',
    '🇬🇧 🤵 Daniel': 'bm_daniel',
}

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = TextProcessor._process_special_cases(text)
        
        re_tab = re.compile(r'[\r\t]')
        re_spaces = re.compile(r' +')
        re_punctuation = re.compile(r'(\s)([,.!?])')
        
        text = re_tab.sub(' ', text)
        text = re_spaces.sub(' ', text)
        text = re_punctuation.sub(r'\2', text)
        return text.strip()

    @staticmethod
    def _process_special_cases(text: str) -> str:
        # Phone numbers: 012-345-6789 -> "zero one two three four five six seven eight nine"
        text = re.sub(r'(\d{3})[-.]?(\d{3})[-.]?(\d{4})', 
                     lambda m: ' '.join([TextProcessor._digit_to_word(d) for d in m.group().replace('-', '').replace('.', '')]), 
                     text)
        
        # Emails: user@domain.com -> "user at domain dot com"
        text = re.sub(r'([\w.-]+)@([\w.-]+)\.(\w+)', 
                     lambda m: f"{m.group(1)} at {m.group(2)} dot {m.group(3)}", 
                     text)
        
        # Websites: www.domain.com -> "www dot domain dot com"
        text = re.sub(r'(https?://|www\.)([\w.-]+)\.(\w+)', 
                     lambda m: f"{m.group(1)} {m.group(2)} dot {m.group(3)}", 
                     text)
        
        # Large numbers: 1,000 -> "one thousand"
        text = re.sub(r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b', 
                     lambda m: TextProcessor._number_to_words(m.group().replace(',', '')), 
                     text)
        
        return text

    @staticmethod
    def _digit_to_word(digit: str) -> str:
        digit_map = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine',
            '.': 'dot', '-': 'dash', '@': 'at', ':': 'colon', '/': 'slash'
        }
        return ' '.join([digit_map.get(c, c) for c in digit])

    @staticmethod
    def _number_to_words(number: str) -> str:
        try:
            if '.' in number:
                integer_part, decimal_part = number.split('.')
                return f"{TextProcessor._int_to_words(integer_part)} point {TextProcessor._digit_to_word(decimal_part)}"
            return TextProcessor._int_to_words(number)
        except:
            return number

    @staticmethod
    def _int_to_words(num_str: str) -> str:
        num = int(num_str)
        if num == 0:
            return 'zero'
        
        units = ['', 'thousand', 'million', 'billion', 'trillion']
        words = []
        level = 0
        
        while num > 0:
            chunk = num % 1000
            if chunk != 0:
                words.append(TextProcessor._convert_less_than_thousand(chunk) + ' ' + units[level])
            num = num // 1000
            level += 1
        
        return ' '.join(reversed(words)).strip()

    @staticmethod
    def _convert_less_than_thousand(num: int) -> str:
        ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
                'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
                'seventeen', 'eighteen', 'nineteen']
        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 
               'eighty', 'ninety']
        
        if num == 0:
            return ''
        if num < 20:
            return ones[num]
        if num < 100:
            return tens[num // 10] + (' ' + ones[num % 10] if num % 10 != 0 else '')
        return ones[num // 100] + ' hundred' + (' ' + TextProcessor._convert_less_than_thousand(num % 100) if num % 100 != 0 else '')

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        re_special_cases = re.compile(r'(?<!\w)([A-Z][a-z]*\.)(?=\s)')
        re_sentence_split = re.compile(r'(?<=[.!?])\s+')
        
        sentences = []
        for line in text.split('\n'):
            stripped = line.strip()
            if stripped:
                stripped = re_special_cases.sub(r'\1Ⓝ', stripped)
                parts = re_sentence_split.split(stripped)
                for part in parts:
                    part = part.replace('Ⓝ', '')
                    if part:
                        sentences.append(part)
        return sentences

class AudioProcessor:
    @staticmethod
    def enhance_audio(audio: np.ndarray) -> np.ndarray:
        max_vol = np.max(np.abs(audio)) + 1e-8
        audio = np.clip(audio / max_vol, -0.99, 0.99)
        
        audio_seg = AudioSegment(
            (audio * 32767).astype(np.int16).tobytes(),
            frame_rate=24000,
            sample_width=2,
            channels=1
        )
        
        audio_seg = normalize(audio_seg)
        audio_seg = compress_dynamic_range(audio_seg, threshold=-20.0, ratio=4.0)
        audio_seg = low_pass_filter(audio_seg, 14000)
        audio_seg = high_pass_filter(audio_seg, 100)
        
        return np.array(audio_seg.get_array_of_samples()) / 32768.0

    @staticmethod
    def calculate_pause(text: str, pause_settings: Dict[str, int]) -> int:
        if not text.strip():
            return 0
        
        re_no_pause = re.compile(
            r'\b(?:Mr|Mrs|Ms|Dr|Prof|St|A\.M|P\.M|etc|e\.g|i\.e)\.',
            re.IGNORECASE
        )
        
        if re_no_pause.search(text):
            return 0
        
        last_char = text.strip()[-1]
        return pause_settings.get(last_char, pause_settings['default_pause'])

    @staticmethod
    def combine_segments(segments: List[AudioSegment], pauses: List[int]) -> AudioSegment:
        combined = AudioSegment.empty()
        
        for i, (seg, pause) in enumerate(zip(segments, pauses)):
            seg = seg.fade_in(20).fade_out(20)
            combined += seg
            
            if i < len(segments) - 1 and pause > 0:
                adjusted_pause = min(pause, len(seg) // 2)
                combined += AudioSegment.silent(duration=adjusted_pause)
        
        return normalize(combined)

class StoryTeller:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.audio_processor = AudioProcessor()

    def generate_sentence_audio(self, sentence: str, voice: str, speed: float,
                              device: str) -> Optional[Tuple[int, np.ndarray]]:
        try:
            voice_code = VOICES.get(voice, voice)
            
            if voice_code not in model_manager.voice_cache:
                pipeline = model_manager.pipelines[voice_code[0]]
                pack = pipeline.load_voice(voice_code)
                model_manager.voice_cache[voice_code] = (pipeline, pack)
            else:
                pipeline, pack = model_manager.voice_cache[voice_code]
            
            for _, ps, _ in pipeline(sentence, voice_code, speed):
                ref_s = pack[len(ps)-1]
                
                if device == 'cuda':
                    ps = ps.cuda()
                    ref_s = ref_s.cuda()
                
                with torch.cuda.amp.autocast(enabled=(device=='cuda')):
                    audio = model_manager.models[device](ps, ref_s, speed).cpu().numpy()
                
                return (24000, self.audio_processor.enhance_audio(audio))
                
        except Exception as e:
            print(f"Error generating audio: {e}")
            if 'CUDA' in str(e) and model_manager.use_cuda:
                return self.generate_sentence_audio(sentence, voice, speed, 'cpu')
            raise gr.Error(f"Audio generation failed: {str(e)}")
        return None

    def generate_story_audio(self, text: str, voice: str, speed: float, device: str,
                           pause_settings: Dict[str, int]) -> Tuple[Tuple[int, np.ndarray], str]:
        start_time = time.time()
        clean_text = self.text_processor.clean_text(text)
        sentences = self.text_processor.split_sentences(clean_text)
        
        if not sentences:
            return None, "No content to read"
        
        audio_segments = []
        pause_durations = []
        
        speed_factor = max(0.7, min(1.3, speed))
        adjusted_pause_settings = {
            'default_pause': int(pause_settings['default_pause'] / speed_factor),
            'dot_pause': int(pause_settings['dot_pause'] / speed_factor),
            'ques_pause': int(pause_settings['ques_pause'] / speed_factor),
            'comma_pause': int(pause_settings['comma_pause'] / speed_factor),
            'colon_pause': int(pause_settings['colon_pause'] / speed_factor),
            'excl_pause': int(pause_settings['dot_pause'] / speed_factor),
            'semi_pause': int(pause_settings['colon_pause'] / speed_factor),
            'dash_pause': int(pause_settings['comma_pause'] / speed_factor)
        }
        
        for sentence in sentences:
            result = self.generate_sentence_audio(sentence, voice, speed, device)
            if not result:
                continue
                
            sample_rate, audio_data = result
            audio_seg = AudioSegment(
                (audio_data * 32767).astype(np.int16).tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )
            audio_segments.append(audio_seg)
            
            pause = self.audio_processor.calculate_pause(sentence, adjusted_pause_settings)
            pause_durations.append(pause)
        
        if not audio_segments:
            return None, "Failed to generate audio"
        
        combined_audio = self.audio_processor.combine_segments(audio_segments, pause_durations)
        
        with io.BytesIO() as buffer:
            combined_audio.export(buffer, format="mp3", bitrate="256k")
            buffer.seek(0)
            audio_data = np.frombuffer(buffer.read(), dtype=np.uint8)
        
        stats = (f"Processed {len(clean_text)} chars, {len(clean_text.split())} words\n"
                f"Time: {time.time() - start_time:.2f}s\n"
                f"Device: {device.upper()}")
        
        return (24000, audio_data), stats

def create_interface():
    css = """
    .gradio-container { max-width: 900px !important; }
    .audio-output { height: 300px !important; }
    .advanced-settings { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
    """
    
    with gr.Blocks(title="Advanced TTS", css=css) as app:
        gr.Markdown("## 🎙️ Advanced TTS - Professional Version")
        
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Input Text",
                    value="Contact us at info@example.com or call 012-345-6789. Our website is https://www.example.com",
                    lines=7
                )
                
                with gr.Accordion("Voice Settings", open=True):
                    voice = gr.Dropdown(
                        label="Select Voice",
                        choices=list(VOICES.keys()),
                        value="🇺🇸 🤵 Adam"
                    )
                    speed = gr.Slider(
                        label="Speed",
                        minimum=0.7,
                        maximum=1.3,
                        value=1.0,
                        step=0.05
                    )
                    device = gr.Radio(
                        label="Processing Device",
                        choices=["GPU 🚀" if CUDA_AVAILABLE else "GPU (Not Available)", "CPU"],
                        value="GPU 🚀" if CUDA_AVAILABLE else "CPU"
                    )
                
                with gr.Accordion("Pause Settings (ms)", open=False):
                    with gr.Row():
                        default_pause = gr.Slider(0, 2000, 200, label="Default")
                        dot_pause = gr.Slider(0, 3000, 600, label="Period (.)")
                        ques_pause = gr.Slider(0, 3000, 800, label="Question (?)")
                    with gr.Row():
                        comma_pause = gr.Slider(0, 1500, 300, label="Comma (,)")
                        colon_pause = gr.Slider(0, 2000, 400, label="Colon (:)")
                
                generate_btn = gr.Button("Generate Speech", variant="primary")
            
            with gr.Column():
                audio_output = gr.Audio(label="Output Audio", elem_classes="audio-output")
                stats_output = gr.Textbox(label="Processing Stats", lines=4)
                gr.Examples(
                    examples=[
                        ["Call 123-456-7890 for support"],
                        ["Email me at john.doe@company.com"],
                        ["Visit https://example.org for more info"],
                        ["The price is $1,234.56"]
                    ],
                    inputs=text_input,
                    label="Special Format Examples"
                )

        storyteller = StoryTeller()

        def generate(text, voice, speed, device, default_pause, dot_pause, ques_pause, comma_pause, colon_pause):
            device = "cuda" if "GPU" in device and CUDA_AVAILABLE else "cpu"
            
            pause_settings = {
                'default_pause': default_pause,
                'dot_pause': dot_pause,
                'ques_pause': ques_pause,
                'comma_pause': comma_pause,
                'colon_pause': colon_pause,
                'excl_pause': dot_pause,
                'semi_pause': colon_pause,
                'dash_pause': comma_pause
            }
            
            result, stats = storyteller.generate_story_audio(
                text, voice, speed, device, pause_settings
            )
            
            if result:
                sample_rate, audio_data = result
                filepath = "/tmp/output.mp3"
                with open(filepath, "wb") as f:
                    f.write(audio_data.tobytes())
                return filepath, stats
            return None, stats

        generate_btn.click(
            fn=generate,
            inputs=[text_input, voice, speed, device, default_pause, dot_pause, ques_pause, comma_pause, colon_pause],
            outputs=[audio_output, stats_output]
        )

    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)