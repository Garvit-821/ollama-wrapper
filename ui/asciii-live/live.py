import cv2
import numpy as np
import pygame
from ultralytics import YOLO

# ================= CONFIG =================
CONFIG = {
    "width": 120,
    "height": 60,
    "colored": True,
    "invert": False,
    "ascii_chars": "@%#*+=-:. ",
    "theme": "green",
    "show_boxes": False
}

ASCII_CHARS = CONFIG["ascii_chars"]

# ================= INIT =================
cap = cv2.VideoCapture(0)
model = YOLO("yolov8n.pt")

pygame.init()
font = pygame.font.SysFont("Courier", 10)
screen = pygame.display.set_mode((900, 650))
pygame.display.set_caption("ASCII Webcam with YOLO Detection")

# ================= FUNCTIONS =================

def get_color(pixel, theme):
    if theme == "green":
        return (0, 255, 0)
    elif theme == "white":
        return (255, 255, 255)
    elif theme == "cyberpunk":
        # Cyberpunk style: magenta/cyan mix based on pixel values
        return (pixel[2] % 255, pixel[1] % 255, pixel[0] % 255)
    return (255, 255, 255)


def frame_to_ascii(frame):
    frame = cv2.resize(frame, (CONFIG["width"], CONFIG["height"]))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ascii_frame = []
    color_frame = []

    for y in range(CONFIG["height"]):
        line = ""
        color_line = []
        for x in range(CONFIG["width"]):
            pixel = gray[y, x]

            if CONFIG["invert"]:
                pixel = 255 - pixel

            # FIXED: Actually assign the character
            char = ASCII_CHARS[int(pixel) * (len(ASCII_CHARS) - 1) // 255]
            line += char

            color_line.append(frame[y, x])

        ascii_frame.append(line)
        color_frame.append(color_line)

    return ascii_frame, color_frame


def detect_objects(frame):
    results = model(frame, verbose=False)
    boxes = []

    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[int(box.cls[0])]
                confidence = float(box.conf[0])
                boxes.append((x1, y1, x2, y2, label, confidence))

    return boxes


def draw_ascii(ascii_frame, color_frame):
    screen.fill((0, 0, 0))

    char_w, char_h = font.size("A")

    for i, line in enumerate(ascii_frame):
        for j, char in enumerate(line):
            x = j * char_w
            y = i * char_h

            # Skip if out of screen bounds
            if x > 900 or y > 650:
                continue

            # Get color based on theme
            if CONFIG["colored"]:
                color = get_color(color_frame[i][j], CONFIG["theme"])
            else:
                color = (255, 255, 255)

            text = font.render(char, True, color)
            screen.blit(text, (x, y))

    pygame.display.flip()


def draw_boxes_preview(frame, boxes):
    """Draw bounding boxes on the original frame for preview"""
    preview_frame = frame.copy()
    for (x1, y1, x2, y2, label, confidence) in boxes:
        cv2.rectangle(preview_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(preview_frame, f"{label} ({confidence:.2f})", 
                   (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Resize preview for display
    preview = cv2.resize(preview_frame, (300, 200))
    cv2.imshow("Detection Preview (Press 'q' to close)", preview)
    return preview


def handle_keys():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_c]:
        CONFIG["colored"] = not CONFIG["colored"]
        print(f"Colored mode: {CONFIG['colored']}")

    if keys[pygame.K_i]:
        CONFIG["invert"] = not CONFIG["invert"]
        print(f"Invert mode: {CONFIG['invert']}")

    if keys[pygame.K_1]:
        CONFIG["theme"] = "green"
        print("Theme: Green")

    if keys[pygame.K_2]:
        CONFIG["theme"] = "white"
        print("Theme: White")

    if keys[pygame.K_3]:
        CONFIG["theme"] = "cyberpunk"
        print("Theme: Cyberpunk")

    if keys[pygame.K_b]:
        CONFIG["show_boxes"] = not CONFIG["show_boxes"]
        print(f"Box detection: {CONFIG['show_boxes']}")


def print_controls():
    """Display controls in console"""
    print("\n" + "="*50)
    print("CONTROLS:")
    print("  C - Toggle color mode")
    print("  I - Toggle invert mode")
    print("  1 - Green theme")
    print("  2 - White theme")
    print("  3 - Cyberpunk theme")
    print("  B - Toggle object detection")
    print("  ESC or Q - Quit")
    print("="*50 + "\n")


# ================= MAIN LOOP =================
print_controls()
running = True
clock = pygame.time.Clock()

while running:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)

    # Convert frame to ASCII
    ascii_frame, color_frame = frame_to_ascii(frame)

    # Object detection
    if CONFIG["show_boxes"]:
        boxes = detect_objects(frame)
        draw_boxes_preview(frame, boxes)
    else:
        # Close OpenCV window if it exists
        try:
            cv2.destroyWindow("Detection Preview (Press 'q' to close)")
        except:
            pass

    # Draw ASCII art
    draw_ascii(ascii_frame, color_frame)

    # Handle keyboard input
    handle_keys()

    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

    # Control frame rate
    clock.tick(30)

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
print("Application closed.")