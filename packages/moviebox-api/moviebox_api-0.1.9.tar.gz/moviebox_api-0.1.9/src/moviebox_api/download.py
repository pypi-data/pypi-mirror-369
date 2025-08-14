"""Contains functionalities for fetching and modelling downloadable files metadata
and later performing the actual download as well
"""

import asyncio
import typing as t
from os import path
from pathlib import Path

import httpx
from tqdm import tqdm

from moviebox_api import logger
from moviebox_api._bases import BaseContentProviderAndHelper, BaseFileDownloaderAndHelper
from moviebox_api.constants import (
    CURRENT_WORKING_DIR,
    DOWNLOAD_QUALITIES,
    DOWNLOAD_REQUEST_HEADERS,
    DownloadMode,
    DownloadQualitiesType,
    DownloadStatus,
    SubjectType,
)
from moviebox_api.exceptions import DownloadCompletedError
from moviebox_api.extractor.models.json import (
    ItemJsonDetailsModel,
    PostListItemSubjectModel,
)
from moviebox_api.helpers import (
    assert_instance,
    get_absolute_url,
    get_filesize_string,
    sanitize_filename,
)
from moviebox_api.models import (
    CaptionFileMetadata,
    DownloadableFilesMetadata,
    MediaFileMetadata,
    SearchResultsItem,
)
from moviebox_api.requests import Session

__all__ = [
    "MediaFileDownloader",
    "CaptionFileDownloader",
    "DownloadableMovieFilesDetail",
    "DownloadableTVSeriesFilesDetail",
    "resolve_media_file_to_be_downloaded",
]


def resolve_media_file_to_be_downloaded(
    quality: DownloadQualitiesType,
    downloadable_metadata: DownloadableFilesMetadata,
) -> MediaFileMetadata:
    """Gets media-file-metadata that matches the target quality

    Args:
        quality (DownloadQualitiesType): Target media quality such
        downloadable_metadata (DownloadableFilesMetadata): Downloadable files metadata

    Raises:
        RuntimeError: Incase media file matching target quality not found
        ValueError: Unexpected target media quality

    Returns:
        MediaFileMetadata: Media file details matching the target media quality
    """
    match quality:
        case "BEST":
            target_metadata = downloadable_metadata.best_media_file
        case "WORST":
            target_metadata = downloadable_metadata.worst_media_file
        case "_":
            if quality in DOWNLOAD_QUALITIES:
                quality_downloads_map = downloadable_metadata.get_quality_downloads_map()
                target_metadata = quality_downloads_map.get(quality)
                if target_metadata is None:
                    raise RuntimeError(
                        f"Media file for quality {quality} does not exists. "
                        f"Try other qualities from {target_metadata.keys()}"
                    )
            else:
                raise ValueError(
                    f"Unknown media file quality passed '{quality}'. Choose from {DOWNLOAD_QUALITIES}"
                )
    return target_metadata


class BaseDownloadableFilesDetail(BaseContentProviderAndHelper):
    """Base class for fetching and modelling downloadable files detail"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/download")

    def __init__(self, session: Session, item: SearchResultsItem | ItemJsonDetailsModel):
        """Constructor for `BaseDownloadableFilesDetail`

        Args:
            session (Session): MovieboxAPI request session.
            item (SearchResultsItem | ItemJsonDetailsModel): Movie/TVSeries item to handle.
        """
        assert_instance(session, Session, "session")
        assert_instance(item, (SearchResultsItem, ItemJsonDetailsModel), "item")
        self.session = session
        self._item: SearchResultsItem | PostListItemSubjectModel = (
            item.resData.postList.items[0].subject if isinstance(item, ItemJsonDetailsModel) else item
        )

    def _create_request_params(self, season: int, episode: int) -> dict:
        """Creates request parameters

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.
        Returns:
            t.Dict: Request params
        """
        return {
            "subjectId": self._item.subjectId,
            "se": season,
            "ep": episode,
        }

    async def get_content(self, season: int, episode: int) -> dict:
        """Performs the actual fetching of files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            t.Dict: File details
        """
        # Referer
        request_header = {"Referer": get_absolute_url(f"/movies/{self._item.detailPath}")}
        # Without the referer, empty response will be served.

        content = await self.session.get_with_cookies_from_api(
            url=self._url,
            params=self._create_request_params(season, episode),
            headers=request_header,
        )
        return content

    async def get_content_model(self, season: int, episode: int) -> DownloadableFilesMetadata:
        """Get modelled version of the downloadable files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            DownloadableFilesMetadata: Modelled file details
        """
        contents = await self.get_content(season, episode)
        return DownloadableFilesMetadata(**contents)


class DownloadableMovieFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model movie files detail"""

    async def get_content(self) -> dict:
        """Actual fetch of files detail"""
        return await super().get_content(season=0, episode=0)

    async def get_content_model(self) -> DownloadableFilesMetadata:
        """Modelled version of the files detail"""
        contents = await self.get_content()
        return DownloadableFilesMetadata(**contents)


class DownloadableTVSeriesFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model series files detail"""

    # NOTE: Already implemented by parent class - BaseDownloadableFilesDetail


class MediaFileDownloader(BaseFileDownloaderAndHelper):
    """Download movie and tv-series files"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}
    movie_filename_template = "%(title)s (%(release_year)d) - %(resolution)dP.%(ext)s"
    series_filename_template = "%(title)s S%(season)dE%(episode)d - %(resolution)dP.%(ext)s"
    # Should have been named episode_filename_template but for consistency
    # with the subject-types {movie, tv-series, music} it's better as it is
    possible_filename_placeholders = (
        "%(title)s",
        "%(release_year)d",
        "%(release_date)s",
        "%(resolution)d",
        "%(ext)s",
        "%(size_string)s",
        "%(season)d",
        "%(episode)d",
    )

    def __init__(self, media_file: MediaFileMetadata):
        """Constructor for `MediaFileDownloader`
        Args:
            session (Session): MovieboxAPI request session.
            media_file (MediaFileMetadata): Movie/tv-series/music to be downloaded.
        """
        assert_instance(media_file, MediaFileMetadata, "media_file")
        self._media_file = media_file
        self.session = httpx.AsyncClient(headers=self.request_headers, cookies=self.request_cookies)
        """Httpx client session for downloading the file"""

    def generate_filename(
        self,
        search_results_item: SearchResultsItem,
        season: int = 0,
        episode: int = 0,
    ) -> str:
        """Generates filename in the format as in `self.*filename_template`

        Args:
            search_results_item (SearchResultsItem)
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            str: Generated filename
        """
        assert_instance(
            search_results_item,
            SearchResultsItem,
            "search_results_item",
        )

        placeholders = dict(
            title=search_results_item.title,
            release_date=str(search_results_item.releaseDate),
            release_year=search_results_item.releaseDate.year,
            ext=self._media_file.ext,
            resolution=self._media_file.resolution,
            size_string=get_filesize_string(self._media_file.size),
            season=season,
            episode=episode,
        )

        filename_template = (
            self.series_filename_template
            if search_results_item.subjectType == SubjectType.TV_SERIES
            else self.movie_filename_template
        )

        return sanitize_filename(filename_template % placeholders)

    async def run(
        self,
        filename: str | SearchResultsItem,
        dir: str | Path = CURRENT_WORKING_DIR,
        progress_bar: bool = True,
        chunk_size: int = 512,
        mode: DownloadMode = DownloadMode.AUTO,
        colour: str = "cyan",
        simple: bool = False,
        test: bool = False,
        leave: bool = True,
        ascii: bool = False,
        suppress_complete_error: bool = False,
        progress_hook: t.Callable = None,
        **kwargs,
    ) -> Path | httpx.Response:
        """Performs the actual download.

        Args:
            filename (str|SearchResultsItem): Movie filename
            dir (str|Path, optional): Directory for saving the contents. Defaults to current working directory.
            progress_bar (bool, optional): Display download progress bar. Defaults to True.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 512.
            mode (DownloadMode, DownloadMode.AUTO): Whether to start fresh download, resume or auto decide the download. Defaults to Auto.
            leave (bool, optional): Keep all leaves of the progressbar. Defaults to True.
            colour (str, optional): Progress bar display color. Defaults to "cyan".
            simple (bool, optional): Show percentage and bar only in progressbar. Deafults to False.
            test (bool, optional): Just test if download is possible but do not actually download. Defaults to False.
            ascii (bool, optional): Use unicode (smooth blocks) to fill the progress-bar meter. Defaults to False.
            suppress_complete_error (bool, optional): Do not raise error when trying to resume a complete download. Defaults to False.
            **kwargs: Keyworded arguments for generating filename incase instance of filename is SearchResultsItem.

        Raises:
            FileExistsError:  Incase of `resume=True` but the download was complete

        Returns:
            str|httpx.Response: Path where the media file has been saved to or httpx Response (test).
        """  # noqa: E501

        assert_instance(mode, DownloadMode, "mode")

        if progress_hook is not None:
            assert callable(progress_hook), (
                f"Value for progress_hook must be a function not {type(progress_hook)}"
            )

        current_downloaded_size = 0
        current_downloaded_size_in_mb = 0

        if isinstance(filename, SearchResultsItem):
            # Lets generate filename
            filename = self.generate_filename(filename, **kwargs)

        save_to = Path(dir) / filename

        match mode:
            case DownloadMode.RESUME:
                resume = True

            case DownloadMode.START:
                resume = False

            case DownloadMode.AUTO:
                resume = save_to.exists()

        def pop_range_in_session_headers():
            if self.session.headers.get("Range"):
                self.session.headers.pop("Range")

        if resume:
            logger.debug("Download set to resume")

            if not path.exists(save_to):
                raise FileNotFoundError(f"File not found in path - '{save_to}'")

            current_downloaded_size = path.getsize(save_to)
            # Set the headers to resume download from the last byte
            self.session.headers.update({"Range": f"bytes={current_downloaded_size}-"})
            current_downloaded_size_in_mb = current_downloaded_size / 1000000

        else:
            logger.debug("Download set to start afresh")

        size_in_bytes = self._media_file.size

        if resume:
            if size_in_bytes == current_downloaded_size:
                if suppress_complete_error:
                    logger.info(f"Download already completed for the file in path - {save_to}")
                    return save_to

                raise DownloadCompletedError(
                    save_to,
                    f"Download completed for the file in path - '{save_to}'",
                )

        size_in_mb = (size_in_bytes / 1_000_000) + current_downloaded_size_in_mb
        size_with_unit = get_filesize_string(self._media_file.size)
        chunk_size_in_bytes = chunk_size * 1_000

        saving_mode = "ab" if resume else "wb"
        logger.info(f"Downloading media file ({size_with_unit}, resume - {resume}). Writing to ({save_to})")

        download_progress = {
            "size": self._media_file.size,
            "size_string": size_with_unit,
            "downloaded_size": current_downloaded_size,
            "dir": dir,
            "filename": filename,
            "path": save_to,
            "status": DownloadStatus.DOWNLOADING,
            "media_file": self._media_file,
            "download_chunk_size": chunk_size_in_bytes,
        }

        async def call_progress_hook(progress: dict):
            if progress_hook is not None:
                if asyncio.iscoroutinefunction(progress_hook):
                    await progress_hook(progress)
                else:
                    progress_hook(progress)

        if progress_bar:
            async with self.session.stream("GET", str(self._media_file.url)) as response:
                response.raise_for_status()

                if test:
                    logger.info(f"Download test passed successfully {response.__repr__}")
                    return response

                with open(save_to, saving_mode) as fh:
                    p_bar = tqdm(
                        desc=f"Downloading{' ' if simple else f' [{filename}]'}",
                        total=round(size_in_mb, 1),
                        unit="Mb",
                        # unit_scale=True,
                        colour=colour,
                        leave=leave,
                        initial=current_downloaded_size_in_mb,
                        ascii=ascii,
                        bar_format=(
                            "{l_bar}{bar} | %(size)s" % (dict(size=size_with_unit))
                            if simple
                            else "{l_bar}{bar}{r_bar}"
                        ),
                    )
                    async for chunk in response.aiter_bytes(chunk_size_in_bytes):
                        fh.write(chunk)

                        current_downloaded_size += chunk_size_in_bytes
                        p_bar.update(round(chunk_size_in_bytes / 1_000_000, 1))
                        download_progress["downloaded_size"] = current_downloaded_size

                        # TODO: Consider eta
                        await call_progress_hook(download_progress)

        else:
            logger.debug(f"Movie file info {self._media_file}")

            async with self.session.stream("GET", str(self._media_file.url)) as response:
                response.raise_for_status()

                if test:
                    logger.info(f"Download test passed successfully {response.__repr__}")
                    return response

                with open(save_to, saving_mode) as fh:
                    async for chunk in response.aiter_bytes(chunk_size_in_bytes):
                        fh.write(chunk)
                        current_downloaded_size += chunk_size_in_bytes
                        download_progress["downloaded_size"] = current_downloaded_size
                        await call_progress_hook(download_progress)

        download_progress["status"] = DownloadStatus.FINISHED
        await call_progress_hook(download_progress)

        logger.info(f"{filename} - {size_with_unit} ✅")
        pop_range_in_session_headers()

        return save_to


class CaptionFileDownloader(BaseFileDownloaderAndHelper):
    """Creates a local copy of a remote subtitle/caption file"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}
    movie_filename_template = (
        "%(title)s (%(release_year)d) - %(lanName)s.%(ext)s"
        # "%(title)s (%(release_year)d) - %(lanName)s [delay - %(delay)d].%(ext)s"
    )
    series_filename_template = "%(title)s S%(season)dE%(episode)d - %(lanName)s.%(ext)s"
    possible_filename_placeholders = (
        "%(title)s",
        "%(release_year)d",
        "%(release_date)s",
        "%(ext)s",
        "%(size_string)s",
        "%(id)s",
        "%(lan)s",
        "%(lanName)s",
        "%(delay)d",
        "%(season)d",
        "%(episode)d",
    )

    def __init__(self, caption_file: CaptionFileMetadata):
        """Constructor for `CaptionFileDownloader`
        Args:
            session (Session): MovieboxAPI request session.
            caption_file (CaptionFileMetadata): Movie/tv-series/music caption file details.
        """
        assert_instance(caption_file, CaptionFileMetadata, "caption_file")
        self._caption_file = caption_file
        self.session = httpx.AsyncClient(headers=self.request_headers, cookies=self.request_cookies)
        """Httpx client session for downloading the file"""

    def generate_filename(
        self,
        search_results_item: SearchResultsItem,
        season: int = 0,
        episode: int = 0,
        **kwargs,
    ) -> str:
        """Generates filename in the format as in `self.*filename_template`

        Args:
            search_results_item (SearchResultsItem)
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Kwargs: Nothing much folk.
                It's just here so that `MediaFileDownloader.run` and `CaptionFileDownloader.run`
                will accept similar parameters in `moviebox_api.extra.movies.Auto.run` method.

        Returns:
            str: Generated filename
        """
        assert_instance(
            search_results_item,
            SearchResultsItem,
            "search_results_item",
        )

        placeholders = dict(
            title=search_results_item.title,
            release_date=str(search_results_item.releaseDate),
            release_year=search_results_item.releaseDate.year,
            ext=self._caption_file.ext,
            lan=self._caption_file.lan,
            lanName=self._caption_file.lanName,
            delay=self._caption_file.delay,
            size_string=get_filesize_string(self._caption_file.size),
            season=season,
            episode=episode,
        )

        filename_template = (
            self.series_filename_template
            if search_results_item.subjectType == SubjectType.TV_SERIES
            else self.movie_filename_template
        )
        return sanitize_filename(filename_template % placeholders)

    async def run(
        self,
        filename: str | SearchResultsItem,
        dir: str = CURRENT_WORKING_DIR,
        chunk_size: int = 16,
        test: bool = False,
        **kwargs,
    ) -> Path | httpx.Response:
        """Performs the actual download, incase already downloaded then return its Path.

        Args:
            filename (str|SearchResultsItem): Movie filename
            dir (str, optional): Directory for saving the contents Defaults to current directory. Defaults to cwd.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 16.
            test (bool, optional): Just test if download is possible but do not actually download. Defaults to False.
            **kwargs: Keyworded arguments for generating filename incase instance of filename is SearchResultsItem.

        Returns:
            Path|httpx.Response: Path where the caption file has been saved to or httpx Response (test).
        """  # noqa: E501
        if isinstance(filename, SearchResultsItem):
            # Lets generate filename
            filename = self.generate_filename(filename, **kwargs)

        save_to = Path(dir) / filename

        if save_to.exists() and path.getsize(save_to) == self._caption_file.size:
            logger.info(f"Caption file already downloaded - {save_to}.")
            return save_to

        size_with_unit = get_filesize_string(self._caption_file.size)

        logger.info(f"Downloading caption file ({size_with_unit}). Writing to ({save_to})")

        async with self.session.stream("GET", str(self._caption_file.url)) as response:
            response.raise_for_status()

            if test:
                logger.info(f"Download test passed successfully {response.__repr__}")
                return response

            with open(save_to, mode="wb") as fh:
                async for chunk in response.aiter_bytes(chunk_size * 1_000):
                    fh.write(chunk)

        logger.info(f"{filename} - {size_with_unit} ✅")
        return save_to
