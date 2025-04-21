import argparse
import asyncio
import os
import webvtt
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips
import edge_tts
from datetime import datetime, timedelta

# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="Generate audio from VTT, split video, adjust segments, and merge.")
    parser.add_argument("--vtt", required=True, help="Path to the input VTT subtitle file")
    parser.add_argument("--video", required=True, help="Path to the input video file")
    parser.add_argument("--output", default="output.mp4", help="Path to the output video file")
    return parser.parse_args()

# 将 VTT 时间格式（HH:MM:SS.mmm）转换为秒
def vtt_time_to_seconds(vtt_time):
    dt = datetime.strptime(vtt_time.split('.')[0], '%H:%M:%S')
    milliseconds = int(vtt_time.split('.')[1])
    return dt.hour * 3600 + dt.minute * 60 + dt.second + milliseconds / 1000

# 将秒转换为 VTT 时间格式
def seconds_to_vtt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"

# 使用 edge-tts 生成音频并返回音频时长
async def generate_audio(text, output_audio, voice="zh-CN-XiaoxiaoNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_audio)
    audio_clip = AudioFileClip(output_audio)
    duration = audio_clip.duration
    audio_clip.close()
    return duration

# 处理 VTT 文件，生成音频和新的 VTT 文件
async def process_vtt(vtt_file, output_audio_dir, output_vtt):
    vtt = webvtt.read(vtt_file)
    new_captions = []
    audio_files = []
    total_duration = 0

    if not os.path.exists(output_audio_dir):
        os.makedirs(output_audio_dir)

    for i, caption in enumerate(vtt):
        text = caption.text
        audio_file = os.path.join(output_audio_dir, f"segment_{i}.mp3")
        duration = await generate_audio(text, audio_file)
        start_time = seconds_to_vtt_time(total_duration)
        end_time = seconds_to_vtt_time(total_duration + duration)
        new_captions.append({
            'start': start_time,
            'end': end_time,
            'text': text
        })
        audio_files.append(audio_file)
        total_duration += duration

    # 写入新的 VTT 文件
    with open(output_vtt, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for caption in new_captions:
            f.write(f"{caption['start']} --> {caption['end']}\n{caption['text']}\n\n")

    # 合并音频
    audio_clips = [AudioFileClip(af) for af in audio_files]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(os.path.join(output_audio_dir, "final_audio.mp3"))
    final_audio.close()
    for clip in audio_clips:
        clip.close()

    # Debugging: Check audio clip durations
    for i, audio_clip in enumerate(audio_clips):
        print(f"Audio clip {i} duration: {audio_clip.duration} seconds")
        if audio_clip.duration == 0:
            print(f"Warning: Audio clip {i} is empty.")

    return audio_files, total_duration

# 分割视频并根据新 VTT 调整长度
def process_video(video_file, vtt_file, new_vtt_file, output_dir):
    vtt = webvtt.read(vtt_file)
    new_vtt = webvtt.read(new_vtt_file)
    video = VideoFileClip(video_file)
    video_segments = []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (old_caption, new_caption) in enumerate(zip(vtt, new_vtt)):
        old_start = vtt_time_to_seconds(old_caption.start)
        old_end = vtt_time_to_seconds(old_caption.end)
        new_start = vtt_time_to_seconds(new_caption.start)
        new_end = vtt_time_to_seconds(new_caption.end)

        # 裁剪视频片段
        segment = video.subclip(old_start, old_end)
        old_duration = old_end - old_start
        new_duration = new_end - new_start

        # 调整速度以匹配新时长
        speed_factor = old_duration / new_duration
        segment = segment.speedx(factor=speed_factor)

        # 保存临时视频片段
        segment_file = os.path.join(output_dir, f"video_segment_{i}.mp4")
        segment.write_videofile(segment_file, codec="libx264", audio_codec="aac")
        video_segments.append(segment_file)
        segment.close()

    video.close()
    return video_segments

# 合并视频和音频
def merge_video_audio(video_segments, audio_file, output_file):
    clips = [VideoFileClip(vs) for vs in video_segments]
    final_video = concatenate_videoclips(clips)
    audio = AudioFileClip(audio_file)
    final_video = final_video.set_audio(audio)
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac")
    final_video.close()
    audio.close()
    for clip in clips:
        clip.close()

# 主函数
async def main():
    args = parse_args()
    output_audio_dir = "temp_audio"
    output_video_dir = "temp_video"
    new_vtt_file = "adjusted.vtt"
    final_audio_file = os.path.join(output_audio_dir, "final_audio.mp3")

    # 处理 VTT 和生成音频
    audio_files, _ = await process_vtt(args.vtt, output_audio_dir, new_vtt_file)

    # 分割视频并调整长度
    video_segments = process_video(args.video, args.vtt, new_vtt_file, output_video_dir)

    # 合并视频和音频
    merge_video_audio(video_segments, final_audio_file, args.output)

    # 清理临时文件
    for af in audio_files:
        if os.path.exists(af):
            os.remove(af)
    for vs in video_segments:
        if os.path.exists(vs):
            os.remove(vs)
    if os.path.exists(final_audio_file):
        os.remove(final_audio_file)
    if os.path.exists(new_vtt_file):
        os.remove(new_vtt_file)
    if os.path.exists(output_audio_dir):
        os.rmdir(output_audio_dir)
    if os.path.exists(output_video_dir):
        os.rmdir(output_video_dir)

if __name__ == "__main__":
    asyncio.run(main())