from typing import Annotated, List, Dict, Union, Optional
from pydantic import Field
from pydantic import BaseModel, model_validator


class VideoMaterial(BaseModel):
    MediaId: Annotated[Optional[str], Field(description="素材ID,与素材URL选填一个")] = None
    MediaURL: Annotated[Optional[str], Field(description="素材URL，与素材ID选填一个")] = None
    In: Annotated[Optional[float], Field(description="素材入点")] = None
    Out: Annotated[Optional[float], Field(description="素材出点")] = None

    @model_validator(mode='after')
    def check_media_id_or_url(self) -> 'VideoMaterial':
        if (self.MediaId is not None) == (self.MediaURL is not None):
            raise ValueError('字段 MediaId 和 MediaURL 必须且只能提供一个')

        return self


class AudioMaterial(BaseModel):
    MediaId: Annotated[Optional[str], Field(description="素材ID,与素材URL选填一个")] = None
    MediaURL: Annotated[Optional[str], Field(description="素材URL，与素材ID选填一个")] = None
    In: Annotated[Optional[float], Field(description="素材入点")] = None
    Out: Annotated[Optional[float], Field(description="素材出点")] = None

    @model_validator(mode='after')
    def check_media_id_or_url(self) -> 'VideoMaterial':
        if (self.MediaId is not None) == (self.MediaURL is not None):
            raise ValueError('字段 MediaId 和 MediaURL 必须且只能提供一个')

        return self


class ImageMaterial(BaseModel):
    MediaId: Annotated[Optional[str], Field(description="素材ID,与素材URL选填一个")] = None
    MediaURL: Annotated[Optional[str], Field(description="素材URL，与素材ID选填一个")] = None

    @model_validator(mode='after')
    def check_media_id_or_url(self) -> 'VideoMaterial':
        if (self.MediaId is not None) == (self.MediaURL is not None):
            raise ValueError('字段 MediaId 和 MediaURL 必须且只能提供一个')

        return self


class SubtitleMaterial(BaseModel):
    MediaId: Annotated[Optional[str], Field(description="素材ID,与素材URL选填一个")] = None
    MediaURL: Annotated[Optional[str], Field(description="素材URL，与素材ID选填一个")] = None

    @model_validator(mode='after')
    def check_media_id_or_url(self) -> 'VideoMaterial':
        if (self.MediaId is not None) == (self.MediaURL is not None):
            raise ValueError('字段 MediaId 和 MediaURL 必须且只能提供一个')

        return self


class MaterialData(BaseModel):
    video_list: Annotated[Optional[List[VideoMaterial]], Field(description="视频素材列表")] = None
    audio_list: Annotated[Optional[List[AudioMaterial]], Field(description="音频素材列表")] = None
    image_list: Annotated[Optional[List[ImageMaterial]], Field(description="图片素材列表")] = None
    subtitle_list: Annotated[Optional[List[SubtitleMaterial]], Field(description="字幕素材列表")] = None


class OutputMediaConfig(BaseModel):
    OutputBucket: Annotated[str, Field(description="输出的OSS bucket名称，示例test-bucket")]
    OutputFileName: Annotated[str, Field(description="输出的OSS文件名，包含文件后缀，示例test.mp4")]
    Width: Annotated[Optional[int], Field(description="输出宽度，单位为像素。")] = None
    Height: Annotated[Optional[int], Field(description="输出高度，单位为像素。")] = None
