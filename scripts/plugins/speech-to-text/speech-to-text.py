from typing import Any
from pytube import YouTube
import os, openai


def load_file_from_youtube_link(url : str) -> str:
    audio = YouTube(url).streams.filter(only_audio=True).first()

    if audio is None:
        raise ValueError("An error occured during the audio extraction with url", url)


    path = "scripts/plugins/speech-to-text/audio_files"
    out_file = audio.download(output_path=path, filename=set_audio_file_name_with_member_name("mariebal#1234"))

    base, ext = os.path.splitext(out_file)
    new_file = base + ".mp3"
    os.rename(out_file, new_file)


    return new_file


def delete_audio_file(path_to_file : str) -> None:
    os.remove(path_to_file)



def get_all_files_from_path(path : str) -> list[str]:
    files : list[str] = []

    for folder, subfolder, files_name in os.walk(path):
        for file_name in files_name:
            files.append(file_name)

    return files


def get_all_member_files(member_name : str, path : str) -> list[str]:
    all_files = get_all_files_from_path(path)

    member_files : list[str] = []
    for file in all_files:
        if member_name in file:
            member_files.append(file)

    return member_files


def set_audio_file_name_with_member_name(member_name : str) -> str:
    member_files = get_all_member_files(member_name, "scripts/plugins/speech-to-text/audio_files")
    if not member_files:
        return f"{member_name} - 0"


    current_file_count = max([int(file[:-4].split(" - ")[1]) for file in member_files])

    return f"{member_name} - {current_file_count + 1}"
    



def transcript_audio_file(file_path : str) -> Any:
    audio_file = open(file_path, "rb")

    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript["text"] #type: ignore


import discord 
from discord.ext import commands
import os, dotenv

dotenv.load_dotenv()
openai.api_key = dotenv.dotenv_values()["OPENAI_API_KEY"]


class SpeechToTextCog(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot 


    @commands.hybrid_command(name="transcribe")
    async def transcribe_youtube_file(self, ctx : commands.Context, *,  url : str) -> discord.Message:
        path = load_file_from_youtube_link("https://www.youtube.com/watch?v=1aA1WGON49E")

        text = transcript_audio_file(path)

        delete_audio_file(path)

        return await ctx.send(text)
        

async def setup(bot : commands.Bot) -> None:
    return await bot.add_cog(SpeechToTextCog(bot))


if __name__ == "__main__":
    pass
