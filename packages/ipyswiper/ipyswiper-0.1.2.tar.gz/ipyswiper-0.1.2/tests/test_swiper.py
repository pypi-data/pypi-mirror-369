from ipyswiper import IpySwiper, create_swiper

import pytest
from ipyswiper.swiper import IpySwiper

@pytest.fixture
def sample_images():
    return [
        {'label': 'Image 1', 'image': 'image1.jpg'},
        {'label': 'Image 2', 'image': 'image2.jpg'}
    ]

def test_swiper_initialization(sample_images):
    swiper = IpySwiper(images=sample_images)
    assert swiper.get_image_count() == 2
    assert swiper.show_labels is True

def test_render_gallery_with_labels(sample_images):
    swiper = IpySwiper(images=sample_images, show_labels=True)
    html = swiper._render_gallery()

    # Check for main image label in the script part
    assert 'const mainLabelHtml = true ? `<div class="main-image-label">${item.label}</div>` : \'\';' in html

    # Check for thumbnail label in the script part
    assert 'const labelHtml = true ? `<div class="thumb-label">${item.label}</div>` : \'\';' in html

def test_render_gallery_without_labels(sample_images):
    swiper = IpySwiper(images=sample_images, show_labels=False)
    html = swiper._render_gallery()

    # Check that labels are disabled in the script part
    assert 'const mainLabelHtml = false ? `<div class="main-image-label">${item.label}</div>` : \'\';' in html
    assert 'const labelHtml = false ? `<div class="thumb-label">${item.label}</div>` : \'\';' in html

def test_swiper_custom_options(sample_images):
    swiper = IpySwiper(
        images=sample_images,
        transition_speed=500,
        transition_effect='fade',
        container_height=800,
        show_labels=False
    )
    html = swiper._render_gallery()
    assert 'speed: 500' in html
    assert "effect: 'fade'" in html
    assert 'height: 800px' in html
    assert 'const mainLabelHtml = false ?' in html