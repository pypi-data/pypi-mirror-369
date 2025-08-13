# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Tuple

import c4d

"""
Functionality used for querying scene settings
"""


class RendererNames(IntEnum):
    """
    A collection of supported renderers and their respective name.
    """

    # native
    standard = 0
    physical = 1023342
    # previewhardware = 300001061  # Not supported for submission

    # 3rd party, now acquired as maxon default
    redshift = 1036219

    # 3rd party
    arnold = 1029988
    vray = 1053272
    corona = 1030480
    cycles = 1035287
    octane = 1029525


class Animation:
    """
    Functionality for retrieving Animation related settings from the active
    document
    """

    @staticmethod
    def current_frame(data) -> int:
        """
        Returns the current frame number from Cinema 4D.
        """
        doc = c4d.documents.GetActiveDocument()
        return int(data[c4d.RDATA_FRAMEFROM].GetFrame(doc.GetFps()))

    @staticmethod
    def start_frame(data) -> int:
        """
        Returns the start frame for the scenes render
        """
        doc = c4d.documents.GetActiveDocument()
        return int(data[c4d.RDATA_FRAMEFROM].GetFrame(doc.GetFps()))

    @staticmethod
    def end_frame(data) -> int:
        """
        Returns the End frame for the scenes Render
        """
        doc = c4d.documents.GetActiveDocument()
        return int(data[c4d.RDATA_FRAMETO].GetFrame(doc.GetFps()))

    @staticmethod
    def frame_step(data) -> int:
        """
        Returns the frame step of the current render.
        """
        return int(data[c4d.RDATA_FRAMESTEP])

    @staticmethod
    def custom_frames(data) -> str:
        """
        Returns the custom frames specification of the current render.
        Note that this field may be filled even if custom frames are not being used.
        To check if custom frames are being used, check whether
        doc.GetActiveRenderData()[c4d.RDATA_FRAMESEQUENCE] == c4d.RDATA_FRAMESEQUENCE_CUSTOM
        """
        return data[c4d.RDATA_FRAME_RANGE_STRING]

    @classmethod
    def frame_list(cls, data=None) -> str:
        """
        Returns a string representing the full framelist.
        """
        if data is None:
            doc = c4d.documents.GetActiveDocument()
            data = doc.GetActiveRenderData()
        frame_spec_type = data[c4d.RDATA_FRAMESEQUENCE]
        if frame_spec_type == c4d.RDATA_FRAMESEQUENCE_CURRENTFRAME:
            return str(FrameRange(start=cls.current_frame(data)))
        if (
            hasattr(c4d, "RDATA_FRAMESEQUENCE_CUSTOM")
            and frame_spec_type == c4d.RDATA_FRAMESEQUENCE_CUSTOM
        ):
            return cls.custom_frames(data)
        return str(
            FrameRange(
                start=cls.start_frame(data), stop=cls.end_frame(data), step=cls.frame_step(data)
            )
        )


class Scene:
    """
    Functionality for retrieving settings from the active scene
    """

    @staticmethod
    def name() -> str:
        """
        Returns the full path to the Active Scene
        """
        doc = c4d.documents.GetActiveDocument()
        return doc[c4d.DOCUMENT_FILEPATH]

    @staticmethod
    def renderer(render_data=None) -> str:
        """
        Returns the name of the current renderer as defined in the scene
        """
        if render_data is None:
            doc = c4d.documents.GetActiveDocument()
            render_data = doc.GetActiveRenderData()
        render_id = render_data[c4d.RDATA_RENDERENGINE]
        return RendererNames(render_id).name

    @staticmethod
    def get_output_directories(render_data=None, take=None) -> set[str]:
        """
        Returns a list of directories files will be output to.
        """
        doc = c4d.documents.GetActiveDocument()
        doc_path = doc.GetDocumentPath()
        if not take:
            take_data = doc.GetTakeData()
            take = take_data.GetCurrentTake()
        render_data = Scene.get_render_data(doc=doc, take=take)

        image_paths = set()
        if render_data[c4d.RDATA_SAVEIMAGE]:
            path = render_data[c4d.RDATA_PATH]
            xpath = Scene.replace_render_path_tokens(
                path, doc=doc, take=take, render_data=render_data
            )
            if not os.path.isabs(xpath):
                if xpath.startswith("./"):
                    xpath = xpath[2:]
                xpath = os.path.join(doc_path, xpath)
            image_paths.add(os.path.dirname(os.path.normpath(xpath)))
        if render_data[c4d.RDATA_MULTIPASS_SAVEIMAGE]:
            path = render_data[c4d.RDATA_MULTIPASS_FILENAME]
            xpath = Scene.replace_render_path_tokens(
                path, doc=doc, take=take, render_data=render_data
            )
            if not os.path.isabs(xpath):
                if xpath.startswith("./"):
                    xpath = xpath[2:]
                xpath = os.path.join(doc_path, xpath)
            image_paths.add(os.path.dirname(os.path.normpath(xpath)))
        return image_paths

    @staticmethod
    def get_render_data(doc=None, take=None):
        if doc is None:
            doc = c4d.documents.GetActiveDocument()
        render_data = None
        if take is not None:
            take_data = doc.GetTakeData()
            take_erd = take.GetEffectiveRenderData(take_data)
            if take_erd is not None:
                render_data = take_erd[0]
        if render_data is None:
            render_data = doc.GetActiveRenderData()
        return render_data

    @staticmethod
    def replace_render_path_tokens(path, doc=None, take=None, render_data=None):
        """
        Replaces tokens in a path with actual values from scene and render data
        """
        if doc is None:
            doc = c4d.documents.GetActiveDocument()

        if render_data is None:
            render_data = Scene.get_render_data(doc=doc, take=take)

        render_path_data = {
            "_doc": doc,
            "_rData": render_data,
            "_rBc": render_data.GetDataInstance(),
            "_frame": doc.GetTime().GetFrame(doc.GetFps()),
        }
        if take:
            render_path_data["_take"] = take

        return c4d.modules.tokensystem.FilenameConvertTokens(path, render_path_data)

    @staticmethod
    def get_output_paths(take=None) -> Tuple[str, str]:
        """
        Returns the default and multi-pass output paths.
        """
        doc = c4d.documents.GetActiveDocument()
        doc_path = doc.GetDocumentPath()
        render_data = Scene.get_render_data(doc=doc, take=take)

        default_out = ""
        multi_out = ""
        if render_data[c4d.RDATA_SAVEIMAGE]:
            path = render_data[c4d.RDATA_PATH]
            xpath = Scene.replace_render_path_tokens(
                path, doc=doc, take=take, render_data=render_data
            )
            if not os.path.isabs(xpath):
                if xpath.startswith("./"):
                    xpath = xpath[2:]
                xpath = os.path.join(doc_path, xpath)
            default_out = os.path.normpath(xpath)
        if render_data[c4d.RDATA_MULTIPASS_SAVEIMAGE]:
            path = render_data[c4d.RDATA_MULTIPASS_FILENAME]
            xpath = Scene.replace_render_path_tokens(
                path, doc=doc, take=take, render_data=render_data
            )
            if not os.path.isabs(xpath):
                if xpath.startswith("./"):
                    xpath = xpath[2:]
                xpath = os.path.join(doc_path, xpath)
            multi_out = os.path.normpath(xpath)
        return default_out, multi_out


@dataclass
class FrameRange:
    """
    Class used to represent a frame range.
    """

    start: int
    stop: Optional[int] = None
    step: Optional[int] = None

    def __repr__(self) -> str:
        if self.stop is None or self.stop == self.start:
            return str(self.start)

        if self.step is None or self.step == 1:
            return f"{self.start}-{self.stop}"

        return f"{self.start}-{self.stop}:{self.step}"
