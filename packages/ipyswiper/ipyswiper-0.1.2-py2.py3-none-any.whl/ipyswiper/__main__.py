import argparse
import json
import sys
from .swiper import IpySwiper

def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(description="Create a standalone HTML image gallery from a JSON file.")

    # Positional and output arguments
    parser.add_argument("json_file", help="Path to the input JSON file.")
    parser.add_argument("-o", "--output", help="Path to the output HTML file. If not provided, prints to stdout.")

    # IpySwiper constructor arguments
    parser.add_argument("--title", default="Image Gallery", help="Title for the HTML page.")
    parser.add_argument("--transition-speed", type=int, default=0, help="Transition speed in milliseconds.")
    parser.add_argument("--transition-effect", default='slide', choices=['slide', 'fade', 'cube', 'coverflow', 'flip'], help="Transition effect.")
    parser.add_argument("--container-height", type=int, default=600, help="Height of the gallery container in pixels.")
    parser.add_argument("--container-max-width", type=int, help="Maximum width of the gallery container in pixels.")
    parser.add_argument("--thumbnail-panel-width", type=int, default=200, help="Width of the thumbnail panel in pixels.")
    parser.add_argument("--thumbnails-per-view", type=int, default=4, help="Number of thumbnails visible at once.")
    parser.add_argument("--thumbnail-fit", default='contain', choices=['cover', 'contain', 'fill'], help="How thumbnails should fit.")
    parser.add_argument("--show-labels", action='store_true', help="Show image labels on thumbnails.")
    parser.add_argument("--use-base64", action='store_true', help="Convert images to base64 data URIs.")
    parser.add_argument("--base-path", default="", help="Base path for relative image paths when using base64.")

    # Custom key arguments
    parser.add_argument("--label-key", default="label", help="JSON key for the image label.")
    parser.add_argument("--image-key", default="image", help="JSON key for the image path.")

    args = parser.parse_args()

    # Load images from JSON file
    try:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            images = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {args.json_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {args.json_file}", file=sys.stderr)
        sys.exit(1)

    # Prepare IpySwiper options
    swiper_options = {
        'transition_speed': args.transition_speed,
        'transition_effect': args.transition_effect,
        'container_height': args.container_height,
        'container_max_width': args.container_max_width,
        'thumbnail_panel_width': args.thumbnail_panel_width,
        'thumbnails_per_view': args.thumbnails_per_view,
        'thumbnail_fit': args.thumbnail_fit,
        'show_labels': args.show_labels,
        'use_base64': args.use_base64,
        'base_path': args.base_path,
        'label_key': args.label_key,
        'image_key': args.image_key,
    }

    # Create IpySwiper instance
    try:
        gallery = IpySwiper(images, **swiper_options)
    except ValueError as e:
        print(f"Error creating gallery: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate and output HTML
    html_content = gallery.save_to_html(filepath=args.output, title=args.title)

    if html_content:
        print(html_content)

if __name__ == "__main__":
    main()
