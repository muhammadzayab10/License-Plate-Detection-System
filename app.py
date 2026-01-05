import gradio as gr
from ultralytics import YOLO
import cv2
import numpy as np
import os

model = YOLO("best.pt")

def detect_plates(file):
    """Automatically detect if input is image or video"""
    if file is None:
        return None, "Please upload a file"
    
    # Check file extension
    file_ext = os.path.splitext(file)[1].lower()
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
        # Process as image
        img = cv2.imread(file)
        results = model(img, verbose=False)
        
        plate_count = 0
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(img, f"Plate: {confidence:.2f}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            plate_count += 1
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        info = f"✅ Image processed: {plate_count} plate(s) detected"
        return img_rgb, info
    
    elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
        # Process as video
        cap = cv2.VideoCapture(file)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_path = "detected_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        total_detections = 0
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            results = model(frame, verbose=False)
            total_detections += len(results[0].boxes)
            
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{confidence:.2f}", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            out.write(frame)
            frame_count += 1
        
        cap.release()
        out.release()
        
        info = f"✅ Video processed: {total_detections} total detections in {frame_count} frames"
        return output_path, info
    
    else:
        return None, "Unsupported file format"

demo = gr.Interface(
    fn=detect_plates,
    inputs=gr.File(label="Upload Image or Video"),
    outputs=[
        gr.File(label="Processed Result"),
        gr.Textbox(label="Info", lines=2)
    ],
    title="🚗 License Plate Detection (Image & Video)",
    description="Upload an image or video to detect license plates"
)

demo.launch()