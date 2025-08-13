import pytest
from unittest.mock import patch, MagicMock
from src.mcp_youtube_extract import youtube
from src.mcp_youtube_extract.server import extract_video_id

# Test get_video_info
@patch('src.mcp_youtube_extract.youtube.build')
def test_get_video_info_success(mock_build):
    mock_youtube = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = {
        'items': [{
            'snippet': {
                'title': 'Test Title',
                'channelTitle': 'Test Channel',
                'publishedAt': '2020-01-01T00:00:00Z',
                'description': 'Test Description'
            }
        }]
    }
    mock_youtube.videos.return_value.list.return_value = mock_request
    mock_build.return_value = mock_youtube
    result = youtube.get_video_info('fake_api_key', 'fake_video_id')
    assert result['snippet']['title'] == 'Test Title'

@patch('src.mcp_youtube_extract.youtube.build')
def test_get_video_info_not_found(mock_build):
    mock_youtube = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = {'items': []}
    mock_youtube.videos.return_value.list.return_value = mock_request
    mock_build.return_value = mock_youtube
    result = youtube.get_video_info('fake_api_key', 'fake_video_id')
    assert result is None

@patch('src.mcp_youtube_extract.youtube.build', side_effect=Exception('API error'))
def test_get_video_info_error(mock_build):
    result = youtube.get_video_info('fake_api_key', 'fake_video_id')
    assert result is None

# Test get_video_transcript
@patch('src.mcp_youtube_extract.youtube.YouTubeTranscriptApi')
def test_get_video_transcript_success(mock_class):
    mock_api_instance = MagicMock()
    mock_class.return_value = mock_api_instance

    mock_transcript = MagicMock()
    mock_transcript.is_generated = True
    mock_transcript.language_code = 'en'
    mock_transcript.fetch.return_value = [{'text': 'Hello world'}]

    mock_list = MagicMock()
    mock_list.__iter__.return_value = iter([mock_transcript])
    mock_list.find_transcript.side_effect = Exception('Not found')

    mock_api_instance.list.return_value = mock_list

    with patch('src.mcp_youtube_extract.youtube.TextFormatter') as mock_formatter:
        mock_formatter.return_value.format_transcript.return_value = 'Hello world'
        result = youtube.get_video_transcript('fake_video_id')
        assert 'Hello world' in result

@patch('src.mcp_youtube_extract.youtube.YouTubeTranscriptApi')
def test_get_video_transcript_no_transcript(mock_class):
    mock_api_instance = MagicMock()
    mock_class.return_value = mock_api_instance

    mock_list = MagicMock()
    mock_list.__iter__.side_effect = StopIteration
    mock_api_instance.list.return_value = mock_list

    result = youtube.get_video_transcript('fake_video_id')
    assert result is None or 'Could not retrieve transcript' in result

@patch('src.mcp_youtube_extract.youtube.YouTubeTranscriptApi')
def test_get_video_transcript_error(mock_class):
    mock_api_instance = MagicMock()
    mock_class.return_value = mock_api_instance

    mock_api_instance.list.side_effect = Exception('API error')

    result = youtube.get_video_transcript('fake_video_id')
    assert 'Could not retrieve transcript' in result

# Test format_video_info
def test_format_video_info_success():
    video_info = {
        'snippet': {
            'title': 'Test Title',
            'channelTitle': 'Test Channel',
            'publishedAt': '2020-01-01T00:00:00Z',
            'description': 'Test Description'
        }
    }
    result = youtube.format_video_info(video_info)
    assert 'Test Title' in result
    assert 'Test Channel' in result
    assert '2020-01-01T00:00:00Z' in result
    assert 'Test Description' in result

def test_format_video_info_none():
    result = youtube.format_video_info(None)
    assert 'Video not found' in result

# Test extract_video_id
@pytest.mark.parametrize("url_or_id, expected_id", [
    ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=60s", "dQw4w9WgXcQ"),
    ("not a valid url", None),
    ("https://www.google.com", None),
])
def test_extract_video_id(url_or_id, expected_id):
    assert extract_video_id(url_or_id) == expected_id
