import os
import json
import base64
import gradio as gr
from datetime import datetime

# -------------------------------
# Core Functions
# -------------------------------

def get_valid_folders(root_path):
    """Scan nested folders and return folders containing PDF, Markdown, and JSON files."""
    valid_folders = []
    for dirpath, _, filenames in os.walk(root_path):
        pdf_files = [f for f in filenames if f.lower().endswith(".pdf")]
        md_files = [f for f in filenames if f.lower().endswith(".md")]
        json_files = [f for f in filenames if f.lower().endswith(".json")]
        if pdf_files and md_files and json_files:
            valid_folders.append(dirpath)
    return valid_folders

def load_folder_by_index(idx, root_path):
    """Load files from a folder by index."""
    folders = get_valid_folders(root_path)
    if not folders or idx >= len(folders):
        return "No PDF found", "No Markdown found", {}, "No folder"

    folder_path = folders[idx]
    pdf_file = next((f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")), None)
    md_file = next((f for f in os.listdir(folder_path) if f.lower().endswith(".md")), None)
    json_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".json")]

    pdf_base64 = None
    if pdf_file:
        with open(os.path.join(folder_path, pdf_file), "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    md_content = ""
    if md_file:
        with open(os.path.join(folder_path, md_file), "r", encoding="utf-8") as f:
            md_content = f.read()

    json_contents = {}
    for jf in json_files:
        with open(os.path.join(folder_path, jf), "r", encoding="utf-8") as f:
            json_contents[jf] = json.load(f)

    pdf_html = (
        f'<iframe src="data:application/pdf;base64,{pdf_base64}" '
        f'width="100%" height="500px"></iframe>'
        if pdf_base64 else "No PDF found"
    )

    return pdf_html, md_content, json_contents, folder_path

def report_error(folder_path, error_msg, error_log_file):
    """Write an error message to the log file."""
    if folder_path == "No folder":
        return "No folder to report"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(error_log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Folder: {folder_path} - Error: {error_msg}\n")
    return f"Error reported for folder: {folder_path}"

# -------------------------------
# Gradio GUI
# -------------------------------

def parser_gui(root_path: str, error_log_file: str):

    folders = get_valid_folders(root_path)

    with gr.Blocks() as demo:
        index_state = gr.State(0)
        loop_done_state = gr.State(False)

        with gr.Row():
            pdf_display = gr.HTML(label="PDF File")
            md_display = gr.Markdown(label="Markdown File")
            json_display = gr.JSON(label="JSON Files")

        folder_display = gr.Textbox(label="Current Folder", interactive=False)
        loop_status_display = gr.Textbox(label="Loop Status", value="", interactive=False)

        with gr.Row():
            next_btn = gr.Button("➡ Next Folder")
            error_input = gr.Textbox(label="Describe Error")
            report_btn = gr.Button("🚨 Report Error")
            report_output = gr.Textbox(label="Report Status", interactive=False)

        # ---------------------------
        # Next folder function
        # ---------------------------
        def next_folder(state_idx, loop_done):
            if not folders:
                return "No PDF found", "No Markdown found", {}, "No folder", 0, ""
            new_idx = state_idx + 1
            if new_idx >= len(folders):
                # Full loop done, stop here
                pdf1, md1, js1, folder_path1 = load_folder_by_index(state_idx, root_path)
                return pdf1, md1, js1, folder_path1, state_idx, "Full loop completed"

            pdf2, md2, js2, folder_path2 = load_folder_by_index(new_idx, root_path)
            return pdf2, md2, js2, folder_path2, new_idx, ""

        next_btn.click(
            fn=next_folder,
            inputs=[index_state, loop_done_state],
            outputs=[pdf_display, md_display, json_display, folder_display, index_state, loop_status_display]
        )

        # ---------------------------
        # Report error function
        # ---------------------------
        report_btn.click(
            fn=lambda folder_path, msg: report_error(folder_path, msg, error_log_file),
            inputs=[folder_display, error_input],
            outputs=report_output
        )

        # ---------------------------
        # Load first folder initially
        # ---------------------------
        if folders:
            pdf, md, js, folder_path = load_folder_by_index(0, root_path)
            pdf_display.value = pdf
            md_display.value = md
            json_display.value = js
            folder_display.value = folder_path

    demo.launch()

# -------------------------------
# Run the GUI
# -------------------------------
if __name__ == "__main__":
    parser_gui(
        root_path=r"C:\Users\JesperThoftIllemannJ\IdeaProjects\testing_gradio_frame\.data",
        error_log_file="error_log.txt"
    )
