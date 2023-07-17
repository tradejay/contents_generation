import os
import sys
import json
import requests

import openai
import gradio as gr

from src.process.shopping import ShoppingDataLoader

preset_title = {0: "네이버 쇼핑 트렌드"}
preset_args = {0:{
                "child_id":"50001420",
                "mid_id":"50000212", 
                "root_id":"50000003", 
                "type_id":"purchase"
                }}

def create_content(user_content, system_content, openai_key):
    openai.api_key = openai_key
    messages = [{"role": "system", "content": system_content},
                {"role": "user", "content": user_content}]
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return chat.choices[0].message.content

def get_preset_template(preset_id):
    if preset_id == 0:
        preset_loader = ShoppingDataLoader(**preset_args[preset_id])

    return preset_loader.get_prompt()


with gr.Blocks() as demo:
    with gr.Row():
        api_key = gr.Textbox(placeholder="sk-...", label="OPENAI_API_KEY", value=None, type="password")
    with gr.Row():
        with gr.Column():
            preset = gr.Dropdown(list(preset_title.values()), type='index', label="Preset")
            # input_data = gr.File(label="제작에 참고할 데이터: txt, csv, json")
            data = gr.Text(label="제작에 참고할 데이터")
        with gr.Column():
            prompt = gr.Textbox(placeholder="컨텐츠 유형과 제작 방향성, 분량 등을 적어주세요.", lines=5, label="제작 요청 사항")
            output = gr.Textbox(interactive=False, lines=5, label="결과물")
    generate = gr.Button("생성하기")

    preset.change(fn=get_preset_template, inputs=preset, outputs=[data, prompt])
    generate.click(fn=create_content, inputs=[prompt, data, api_key], outputs=output)
    
demo.launch()