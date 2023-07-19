import os
import sys
import json
import requests

import openai
import gradio as gr

from src.process.shopping import ShoppingPromptTool

import gradio as gr

theme = gr.themes.Default(
    primary_hue="blue",
).set(
    block_shadow='none',
    block_shadow_dark='none',
    form_gap_width='0px',
    checkbox_label_background_fill='*button_secondary_background_fill',
    checkbox_label_background_fill_dark='*button_secondary_background_fill',
    checkbox_label_background_fill_hover='*button_secondary_background_fill_hover',
    checkbox_label_background_fill_hover_dark='*button_secondary_background_fill_hover',
    checkbox_label_shadow='none',
    error_background_fill_dark='*background_fill_primary',
    input_background_fill='*neutral_100',
    input_background_fill_dark='*neutral_700',
    input_border_width='0px',
    input_border_width_dark='0px',
    input_shadow='none',
    input_shadow_dark='none',
    input_shadow_focus='*input_shadow',
    input_shadow_focus_dark='*input_shadow',
    stat_background_fill='*primary_300',
    stat_background_fill_dark='*primary_500',
    button_shadow='none',
    button_shadow_active='none',
    button_shadow_hover='none',
    button_transition='background-color 0.2s ease',
    button_primary_background_fill='*primary_200',
    button_primary_background_fill_dark='*primary_700',
    button_primary_background_fill_hover='*button_primary_background_fill',
    button_primary_background_fill_hover_dark='*button_primary_background_fill',
    button_primary_border_color_dark='*primary_600',
    button_secondary_background_fill='*neutral_200',
    button_secondary_background_fill_dark='*neutral_600',
    button_secondary_background_fill_hover='*button_secondary_background_fill',
    button_secondary_background_fill_hover_dark='*button_secondary_background_fill',
    button_cancel_background_fill='*button_secondary_background_fill',
    button_cancel_background_fill_dark='*button_secondary_background_fill',
    button_cancel_background_fill_hover='*button_cancel_background_fill',
    button_cancel_background_fill_hover_dark='*button_cancel_background_fill',
    button_cancel_border_color='*button_secondary_border_color',
    button_cancel_border_color_dark='*button_secondary_border_color',
    button_cancel_text_color='*button_secondary_text_color',
    button_cancel_text_color_dark='*button_secondary_text_color'
)

title_preset = {0: "네이버 쇼핑 트렌드"}
item_preset  = {0: {"상품" : ["선풍기", "블랙박스", "냉장고"],
                  "순위 유형": ["많이 본 상품", "많이 구매한 상품", "인기 브랜드", "트렌드 키워드"]}}
script_preset = {0: "간단히 요약하기",
                 1: "호기심을 유발하기"}

def create_content(tool, openai_key):
    openai.api_key = openai_key
    system_content, user_content = tool.get_fullprompt()
    messages = [{"role": "system", "content": system_content},
                {"role": "user", "content": user_content}]
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return chat.choices[0].message.content

def get_tool(preset_id):
    if preset_id == 0:
        tool = ShoppingPromptTool()
    return tool

def get_itemlist(preset_id):
    params = list(item_preset[preset_id].items())
    is_interactive = [True if len(_) > 0 else False for _ in item_preset[preset_id].values()]
    return param1.update(choices=params[0][1], label=params[0][0], interactive=is_interactive[0]), \
        param2.update(choices=params[1][1], label=params[1][0], interactive=is_interactive[1])

def load_data(dataloader, *args):    
    args = (_ for _ in args if len(_) > 0)
    data, prompt = dataloader(*args)
    return data, prompt

def get_image_file(tool):
    tool.save_image()

with gr.Blocks(theme=theme) as demo:
    with gr.Row():
        with gr.Column(variant="panel"):
            gr.Markdown("## 1 컨텐츠 내용 선정하기")
            content_titles = gr.Dropdown(list(title_preset.values()), info="주제를 선택하세요.", type='index', label="주제")
            with gr.Row(variant="compact") as item_params:
                param1 = gr.Dropdown([], visible=True, interactive=False, label="세부 주제1")
                param2 = gr.Dropdown([], visible=True, interactive=False, label="세부 주제2")
            prompt_type = gr.Dropdown(list(script_preset.values()), info="어떤 컨텐츠를 만들고 싶은지 선택하세요.", type='index', label="스크립트 스타일")
            tool = gr.State()
            with gr.Accordion("데이터 직접 업로드하기", open=False):
                data_file = gr.File(label="Local file")
            btn_data = gr.Button("데이터와 프롬프트 가져오기", variant="secondary")
        with gr.Column():
            gr.Markdown("## 2 스크립트 만들기")
            data = gr.Text(label="컨텐츠 관련 자료", max_lines=5)
            prompt = gr.Textbox(interactive=True, max_lines=1, label="프롬프트")
            api_key = gr.Textbox(placeholder="sk-...", label="OPENAI_API_KEY", value=None, type="password")
            output = gr.Textbox(interactive=False, max_lines=5, label="스크립트", show_copy_button=True)
    generate = gr.Button("스크립트 생성하기", variant="primary")
    with gr.Row():
        save_image = gr.Button("컨텐츠 이미지 저장하기")
        save_data = gr.Button("컨텐츠 이미지 저장하기")
        save_prompt = gr.Button("프롬프트 저장하기")

    content_titles.change(fn=get_tool, inputs=[content_titles], outputs=[tool]).then(get_itemlist, [content_titles], [param1, param2])
    btn_data.click(fn=load_data, inputs=[tool, param1, param2], outputs=[data, prompt])
    generate.click(fn=create_content, inputs=[tool, api_key], outputs=output)
    save_image.click(fn=get_image_file, inputs=[tool])
    
if __name__ == "__main__":
    demo.queue(concurrency_count=10).launch()