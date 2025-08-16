import sys
import os
import re
import requests
import click
import json
from bs4 import BeautifulSoup as bs
from requests import Session
from llvd import config
from llvd.exceptions import EmptyCourseList
from llvd.downloader import download_subtitles, download_video, download_exercises
from click_spinner import spinner
import re
from llvd.utils import clean_name, cleanup_empty_directories
import click
import sys
from llvd import config
import subprocess
import datetime
import time


class App:
    def __init__(
        self, email, password, course_slug, resolution, caption, exercise, throttle, proxies=None
    ):
        self.email = email
        self.password = password
        self.course_slug = course_slug[0]
        self.course_download_dir = f"./{self.course_slug}"
        self.downloaded_videos = set()
        self._load_downloaded_videos()
        self.course_type = course_slug[1]
        self.link = ""
        self.video_format = resolution
        self.caption = caption
        self.exercise = exercise
        self.cookies = {}
        self.headers = {}
        self.chapter_path = ""
        self.current_video_index = None
        self.current_chapter_index = None
        self.current_video_name = ""
        self.throttle = throttle
        self.debug_mode = True
        
        # Initialize proxy support
        self.proxies = proxies or []
        self.current_proxy_idx = 0
        
        # Initialize summary tracking
        self.summary = {
            'courses_processed': 0,
            'videos': {
                'total': 0,
                'downloaded': 0,
                'skipped': 0,
                'failed': 0,
                'already_exist': 0
            },
            'chapters': {
                'total': 0,
                'empty': 0,
                'deleted': 0
            },
            'errors': []
        }
        
        # Initialize summary tracking
        self.summary = {
            'courses_processed': 0,
            'videos': {
                'total': 0,
                'downloaded': 0,
                'skipped': 0,
                'failed': 0,
                'already_exist': 0
            },
            'chapters': {
                'total': 0,
                'empty': 0,
                'deleted': 0
            },
            'errors': []
        }
        
    def _load_downloaded_videos(self):
        """Load the set of already downloaded videos"""
        self.downloaded_videos = set()
        if not os.path.exists(self.course_download_dir):
            return

        for root, _, files in os.walk(self.course_download_dir):
            for file in files:
                if file.endswith(".mp4"):
                    # Extract the video name without extension and any numbering
                    video_name = os.path.splitext(file)[0]
                    # Remove any numbering at the start (e.g., '01. ')
                    video_name = re.sub(r"^\d+\.\s*", "", video_name)
                    self.downloaded_videos.add(video_name)

    def _is_video_downloaded(self, video_name):
        """Check if a video has already been downloaded"""
        clean_video_name = re.sub(r'[\\/*?:"<>|]', "", video_name)
        return clean_video_name in self.downloaded_videos

    def _mark_video_downloaded(self, video_name):
        """Mark a video as downloaded"""
        clean_video_name = re.sub(r'[\\/*?:"<>|]', "", video_name)
        self.downloaded_videos.add(clean_video_name)

    def login(self, session, login_data):

        try:
            with spinner():

                session.post(config.signup_url, login_data)
                cookies = session.cookies.get_dict()
                self.cookies["JSESSIONID"] = cookies.get("JSESSIONID").replace('"', "")
                self.cookies["li_at"] = cookies.get("li_at")
                self.headers["Csrf-Token"] = cookies.get("JSESSIONID").replace('"', "")

                if cookies.get("li_at") == None:
                    return None
                return 200

        except ConnectionResetError:
            click.echo(
                click.style(
                    f"ConnectionResetError: There is a connection error. Please check your connectivity.\n",
                    fg="red",
                )
            )

        except requests.exceptions.ConnectionError:
            click.echo(
                click.style(
                    f"ConnectionError: There is a connection error. Please check your connectivity.\n",
                    fg="red",
                )
            )

    def get_session(self):
        session = Session()
        if self.proxies:
            click.echo(click.style("\nUsing proxies for requests", fg="green"))
            proxy = self.proxies() if callable(self.proxies) else self.proxies
            session.proxies = {
                "http": proxy,
                "https": proxy,
            }
        return session

    def run(self, cookies=None, headers={}):
        """
        Main function, tries to login the user and when it succeeds, tries to download the course
        """
        try:

            if cookies is not None:
                self.cookies["JSESSIONID"] = cookies.get("JSESSIONID")
                self.cookies["li_at"] = cookies.get("li_at")

                self.headers = headers
                self.headers["Csrf-Token"] = cookies.get("JSESSIONID")

                # remove empty files
                command = "find . -depth -type f -size 0 -exec rm {} +"
                subprocess.run(command, shell=True)

                # proceed to download
                self.download()
            else:
                with self.get_session() as session:
                    site = session.get(config.login_url)
                    bs_content = bs(site.content, "html.parser")

                    csrf = bs_content.find("input", {"name": "csrfToken"}).get("value")
                    loginCsrfParam = bs_content.find(
                        "input", {"name": "loginCsrfParam"}
                    ).get("value")
                    login_data = {
                        "session_key": self.email,
                        "session_password": self.password,
                        "csrfToken": csrf,
                        "loginCsrfParam": loginCsrfParam,
                    }

                    status = self.login(session, login_data)

                    if status is None:
                        click.echo(
                            click.style(f"Wrong credentials, try again", fg="red")
                        )
                        sys.exit(0)
                    else:
                        self.create_course_dirs(self.course_slug)
                        self.download()

        except ConnectionError:
            click.echo(click.style(f"ConnectionError: Failed to connect", fg="red"))

    @staticmethod
    def create_course_dirs(course_slug):
        """
        Create file system path for courses
        """
        if not os.path.exists(f"{course_slug}"):
            os.makedirs(f"{course_slug}")

    @staticmethod
    def remove_failed_downloads():
        """Remove failed downloads."""

    failed_files = [
        file for file in os.listdir() if ".mp4" in file and os.stat(file).st_size == 0
    ]
    if failed_files:
        for file in failed_files:
            os.remove(file)
        click.echo(click.style("Resuming download..", fg="red"))

    def download(self):
        """
        Determines whether to download from learning path
        or from a course directly.
        """
        PATH = "path"
        try:
            if self.course_type == PATH:
                self.download_courses_from_path()
            else:
                self.download_entire_course()
        except TypeError as e:
            print("retrying...")
            self.download_entire_course()

        except ConnectionResetError:
            self._start_modified_spinner("...")
            if self.debug_mode:
                self._save_debug_info(e, self.course_slug, "download")

        except requests.exceptions.ConnectionError:
            self._start_modified_spinner("...")
            if self.debug_mode:
                self._save_debug_info(e, self.course_slug, "download")

    def download_courses_from_path(self):
        try:
            page_url = config.path_url.format(self.course_slug)
            with self.get_session() as session:
                page = session.get(page_url)
            soup = bs(page.content, "html.parser")
            course_list = soup.select('script[type="application/ld+json"]')

            if not course_list:
                raise EmptyCourseList
            else:
                course_list = course_list[0]

            course_list = json.loads(course_list.string.replace("\n", ""))
            total_courses = len(course_list["itemListElement"])
            click.echo(
                f"Downloading {total_courses} courses from learning-path: {self.course_slug}\n"
            )

            for index, course in enumerate(course_list["itemListElement"]):
                course_token = course["item"]["url"].split("/")[-1]
                suppress = index + 1 != total_courses
                click.echo(
                    f"\nDownloading course {index+1}/{total_courses}: {course_token}"
                )
                self.course_slug = course_token
                self.create_course_dirs(course_token)
                self.download_entire_course(skip_done_alert=suppress)

        except EmptyCourseList as e:
            self._start_modified_spinner("...")
            if self.debug_mode:
                self._save_debug_info(e, self.course_slug, "download_courses_from_path")

        except Exception as e:
            self._start_modified_spinner("...")
            if self.debug_mode:
                self._save_debug_info(e, self.course_slug, "download_courses_from_path")

    def fetch_video(self, video):
        """
        Fetch video data in the highest available resolution (1080p with fallback to 720p)
        and save response for debugging if in debug mode
        """
        video_name = re.sub(r'[\\/*?:"<>|]', "", video["title"])
        self.current_video_name = video_name
        video_slug = video["slug"]
        original_format = self.video_format  # <-- Add this line

        resolutions_to_try = [self.video_format]
        if self.video_format == "1080":
            resolutions_to_try = ["1080", "720"]

        last_exception = None
        page_json = None
        download_url = None
        download_success = False

        for resolution in resolutions_to_try:
            self.video_format = resolution
            video_url = config.video_url.format(
                self.course_slug, resolution, video_slug
            )

            try:
                with self.get_session() as session:
                    page_data = session.get(
                        video_url,
                        cookies=self.cookies,
                        headers=self.headers,
                        allow_redirects=False,
                        timeout=30
                    )
                try:
                    page_json = page_data.json()
                    # Check for locked/premium content
                    if "elements" in page_json and page_json["elements"] and \
                       isinstance(page_json["elements"][0], dict):
                        
                        element = page_json["elements"][0]
                        is_locked = element.get("isLocked", False) or element.get("lockedState") == "LOCKED"
                        requires_subscription = element.get("requiresSubscription", False)
                        
                        if is_locked or requires_subscription:
                            error_info = {
                                "status": "locked_content",
                                "url": video_url,
                                "is_locked": is_locked,
                                "requires_subscription": requires_subscription,
                                "video_slug": video_slug,
                                "video_name": video_name,
                                "response_metadata": {
                                    "status_code": page_data.status_code,
                                    "content_type": page_data.headers.get("content-type")
                                }
                            }
                            if self.debug_mode:
                                self._save_debug_info(
                                    {**error_info, "full_response": page_json},
                                    video_slug,
                                    "locked_content"
                                )
                            raise ValueError("This video is locked or requires a premium subscription")
                    
                    # Save successful response for debugging
                    if self.debug_mode and page_data.status_code == 200:
                        self._save_debug_info(
                            {
                                "status": "success",
                                "url": video_url,
                                "resolution": resolution,
                                "response": page_json,
                                "video_slug": video_slug,
                                "video_name": video_name,
                                "headers": dict(page_data.headers),
                                "status_code": page_data.status_code
                            },
                            video_slug,
                            f"success_{resolution}p"
                        )
                    
                    download_url = self._extract_video_url(page_json, video_slug, video_name)
                    if not download_url:
                        if resolution == "1080" and "720" in resolutions_to_try:
                            continue
                        raise ValueError("No video URL found")
                    break
                except ValueError as e:
                    last_exception = e
                    if resolution == "1080" and "720" in resolutions_to_try:
                        continue
                    raise
            except requests.exceptions.RequestException as e:
                last_exception = e
                if resolution == "1080" and "720" in resolutions_to_try:
                    continue
                raise
        else:
            if last_exception:
                raise last_exception
            raise ValueError("Failed to fetch video data")

        # Get subtitles if available (from the last successful response)
        subtitles = page_json["elements"][0].get("selectedVideo", {}).get("transcript")
        duration_in_ms = int(page_json["elements"][0].get("selectedVideo", {}).get("durationInSeconds", 0)) * 1000

        click.echo(
            click.style(
                f"\nCurrent: {self.current_chapter_index:02d}. {self.chapter_path.split('/')[-1]}/"
                f"{self.current_video_index:02d}. {video_name}.mp4 @{resolution}p"
            )
        )
        try:
            download_success = download_video(
                download_url,
                self.current_video_index,
                video_name,
                self.chapter_path,
                self.throttle,
            )

            # Only try to download subtitles if video download was successful
            if subtitles and self.caption and download_success:
                try:
                    download_subtitles(
                        self.current_video_index,
                        subtitles.get("lines", []),
                        video_name,
                        self.chapter_path,
                        duration_in_ms,
                    )
                except Exception as e:
                    click.echo(click.style(
                        f"[WARNING] Failed to download subtitles: {str(e)}",
                        fg="yellow"
                    ))

        except Exception as e:
            self._start_modified_spinner("...")
            if self.debug_mode:
                self._save_debug_info(
                    {
                        "status": "download_failed",
                        "url": download_url,
                        "resolution": resolution,
                        "error": str(e),
                        "video_slug": video_slug,
                        "video_name": video_name
                    },
                    video_slug,
                    "download_failed"
                )
            raise
        finally:
            # Restore the original video format
            self.video_format = original_format

        return page_json, video_name, download_success

    def _extract_video_url(self, page_json, video_slug, video_name):
        """Extract video URL from the JSON response with multiple fallback methods"""
        if not page_json or "elements" not in page_json or not page_json["elements"]:
            return None

        element = page_json["elements"][0]
        selected_video = element.get("selectedVideo", {})
        
        # Method 1: Get from selectedVideo.url.progressiveUrl
        if selected_video.get("url") and isinstance(selected_video["url"], dict):
            download_url = selected_video["url"].get("progressiveUrl")
            if download_url:
                return download_url
        
        # Method 2: Check video formats array
        if selected_video.get("formats"):
            for fmt in selected_video["formats"]:
                if fmt.get("type") == "progressive" and fmt.get("url"):
                    return fmt["url"]
            if selected_video["formats"] and selected_video["formats"][0].get("url"):
                return selected_video["formats"][0]["url"]
        
        # Method 3: Check alternative locations
        if "video" in element and "playback" in element["video"]:
            playback = element["video"]["playback"]
            if isinstance(playback, dict):
                return playback.get("progressiveUrl") or playback.get("url")
        
        # Save debug info if no URL found
        if self.debug_mode:
            self._save_debug_info(
                {
                    "status": "no_video_url_found",
                    "element_keys": list(element.keys()) if isinstance(element, dict) else [],
                    "selected_video_keys": list(selected_video.keys()) if isinstance(selected_video, dict) else []
                },
                video_slug,
                "no_video_url"
            )
        
        return None

    def _save_debug_info(self, response_data, video_slug, error_type):
        """Save debug information for failed downloads"""
        debug_dir = os.path.join(self.course_download_dir, "_debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{video_slug}_{error_type}.json"
        filepath = os.path.join(debug_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            click.echo(f"[DEBUG] Failed to save debug info: {str(e)}")
            return None

    def fetch_chapter(self, chapter, chapters_pad_length, delay):
        chapter_name = chapter["title"]
        videos = chapter["videos"]
        chapters_index_padded = str(self.current_chapter_index).rjust(
            chapters_pad_length, "0"
        )
        chapter_path = os.path.join(
            self.course_download_dir, 
            f"{chapters_index_padded}. {clean_name(chapter_name)}"
        )
        video_index = 1
        self.chapter_path = chapter_path
        
        # Update summary
        self.summary['chapters']['total'] += 1
        
        if not os.path.exists(chapter_path):
            os.makedirs(chapter_path)

        current_files = []
        for file in os.listdir(chapter_path):
            if file.endswith(".mp4") and ". " in file:
                ff = re.split(r"\d+\. ", file)[1].replace(".mp4", "")
                current_files.append(ff)

        # Filter out already downloaded videos
        videos_to_download = []
        for video in videos:
            video_name = re.sub(r'[\\/*?:"<>|]', "", video["title"])
            if clean_name(video_name) not in current_files:
                videos_to_download.append(video)
            else:
                self.summary['videos']['already_exist'] += 1
        
        self.summary['videos']['total'] += len(videos)

        # Track how many videos were downloaded in this chapter
        downloaded_in_chapter = 0

        for video in videos_to_download:
            self.current_video_index = video_index + len(current_files)
            video_name = re.sub(r'[\\/*?:"<>|]', "", video["title"])
            video_slug = video.get("slug")
            self.current_video_name = video_name
            
            if not video_slug:
                click.echo(click.style(
                    f"[WARNING] Video '{video_name}' has no slug, skipping...", 
                    fg="yellow"
                ))
                self._save_debug_info(video, "no_slug", "missing_slug")
                self.summary['videos']['skipped'] += 1
                video_index += 1
                continue

            try:
                # Fetch video data
                try:
                    page_json, video_name, download_success = self.fetch_video(video)
                except ValueError as e:
                    if "locked" in str(e).lower() or "premium" in str(e).lower():
                        click.echo(click.style(
                            f"[WARNING] {str(e)} - Skipping video: {video_name}", 
                            fg="yellow"
                        ))
                        self.summary['videos']['skipped'] += 1
                        video_index += 1
                        continue
                    raise
                
                # Extract video URL using the helper method
                download_url = self._extract_video_url(page_json, video_slug, video_name)
                if not download_url:
                    click.echo(click.style(
                        f"[ERROR] Could not find video URL for '{video_name}'", 
                        fg="red"
                    ))
                    self._save_debug_info(page_json, video_slug, "no_video_url")
                    self.summary['videos']['failed'] += 1
                    video_index += 1
                    continue

                # Mark video as successfully downloaded
                if download_success:
                    self._mark_video_downloaded(video_name)
                    self.summary['videos']['downloaded'] += 1
                    downloaded_in_chapter += 1  # <-- Track successful downloads
                else:
                    self.summary['videos']['failed'] += 1

            except Exception as e:
                self._start_modified_spinner("...")
                self.summary['videos']['failed'] += 1
                self.summary['errors'].append(f"Error processing '{video_name}': {str(e)}")
                if self.debug_mode:
                    self._save_debug_info(
                        {"error": str(e), "video": video}, 
                        video_slug, 
                        "processing_error"
                    )
            video_index += 1

        # Optionally, still check if the directory is empty and log an error if so
        try:
            entries = os.listdir(chapter_path)
            if not entries:
                # Directory is empty, but this should be rare now
                pass
        except OSError as e:
            self.summary['errors'].append(f"Error checking chapter directory {chapter_path}: {str(e)}")
        
        # After all downloads, check if the chapter is truly empty (no .mp4 files at all)
        try:
            mp4_files = [f for f in os.listdir(chapter_path) if f.endswith(".mp4")]
            if len(videos) > 0 and not mp4_files:
                self.summary['chapters']['empty'] += 1
        except OSError as e:
            self.summary['errors'].append(f"Error checking chapter directory {chapter_path}: {str(e)}")

    def download_entire_course(self, *args, **kwargs):
        skip_done_alert = kwargs.get("skip_done_alert", False)
        try:
            self._start_spinner("Initializing course download...")
            course_url = config.course_url.format(self.course_slug)
            r = self._request_with_proxies(
                "get",
                course_url,
                cookies=self.cookies,
                headers=self.headers,
                allow_redirects=True,
            )
            try:
                response_json = r.json()

                if "elements" not in response_json or not response_json["elements"]:
                    error_msg = "The course data could not be retrieved. This might be due to authentication issues or the course might not be accessible."
                    self.summary['errors'].append(error_msg)
                    self._stop_spinner()
                    click.echo(click.style(error_msg, fg="red"))
                    return False

                course_data = response_json["elements"][0]
                course_name = course_data.get("title", "Unknown Course")

                if "chapters" not in course_data or not course_data["chapters"]:
                    error_msg = "No chapters found in the course."
                    self.summary['errors'].append(error_msg)
                    self._stop_spinner()
                    click.echo(click.style(error_msg, fg="red"))
                    return False

                # Store the chapters list in the instance
                self.chapters = course_data["chapters"]
                self._stop_spinner()
                
                # Print course info
                click.echo(click.style(f"\nCourse: {course_name}", fg="cyan", bold=True))
                click.echo(click.style(f"Chapters: {len(self.chapters)}", fg="cyan"))
                click.echo("-" * 50)

                # Calculate padding for chapter numbers
                chapters_pad_length = len(str(len(self.chapters)))

                # Process each chapter
                for i, chapter in enumerate(self.chapters, 1):
                    self.current_chapter_index = i
                    try:
                        self.fetch_chapter(chapter, chapters_pad_length, self.throttle)
                    except Exception as e:
                        error_msg = f"Error processing chapter {i}: {str(e)}"
                        self.summary['errors'].append(error_msg)
                        self._stop_spinner()
                        click.echo(click.style(f"\n{error_msg}", fg="red"))
                        continue

                # Clean up empty directories
                deleted_dirs = cleanup_empty_directories(self.course_download_dir)
                self.summary['chapters']['deleted'] = deleted_dirs
                
                if not skip_done_alert:
                    self._stop_spinner()
                    click.echo(click.style("\n✓ Download completed", fg="green", bold=True))
                
                return True

            except json.JSONDecodeError as e:
                error_msg = "Failed to parse course data. The course might be locked or not accessible."
                self.summary['errors'].append(error_msg)
                self._stop_spinner()
                click.echo(click.style(error_msg, fg="red"))
                return False

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.summary['errors'].append(error_msg)
            self._stop_spinner()
            click.echo(click.style(f"\n✗ {error_msg}", fg="red"))
            return False
            
        finally:
            # Ensure spinner is always stopped
            self._stop_spinner()
            # Print summary only if we're not in a nested call (when processing learning paths)
            if not skip_done_alert:
                self._print_summary()

    def _get_next_proxy(self):
        """Get the next proxy from the list in a round-robin fashion"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_proxy_idx]
        self.current_proxy_idx = (self.current_proxy_idx + 1) % len(self.proxies)
        return {
            'http': proxy,
            'https': proxy,
        }

    def _make_request(self, method, url, **kwargs):
        """Wrapper around requests to handle proxy rotation and retries"""
        max_retries = len(self.proxies) if self.proxies else 1
        last_exception = None
        
        for attempt in range(max_retries):
            proxy = self._get_next_proxy()
            try:
                if proxy:
                    kwargs['proxies'] = proxy
                    if self.debug_mode:
                        click.echo(click.style(f"Using proxy: {proxy}", fg="cyan"))
                
                if method.upper() == 'GET':
                    response = requests.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = requests.post(url, **kwargs)
                elif method.upper() == 'PUT':
                    response = requests.put(url, **kwargs)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if self.debug_mode:
                    click.echo(click.style(f"Attempt {attempt + 1} failed with proxy {proxy}: {str(e)}", fg="yellow"))
                continue
        
        # If we get here, all retries failed
        if last_exception:
            if self.debug_mode:
                click.echo(click.style(f"All proxy attempts failed. Last error: {str(last_exception)}", fg="red"))
            raise last_exception
            
        raise Exception("Failed to make request")

    def _print_summary(self):
        """Print a formatted summary of the download process in a table format"""
        summary = self.summary
        
        # Don't print summary if there's no data
        if not any(summary.values()):
            return
            
        from texttable import Texttable
        
        # Initialize table with a border
        table = Texttable()
        table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(["l", "r"])
        table.set_cols_valign(["m", "m"])
        
        # Add title
        table.add_row(["DOWNLOAD SUMMARY", ""])
        table.add_row(["-" * 30, "-" * 10])
        
        # Add course summary if available
        if summary['courses_processed'] > 0:
            table.add_row(["Courses processed:", summary['courses_processed']])
        
        # Add video summary
        table.add_row(["\nVIDEOS", ""])
        table.add_row(["  • Total", summary['videos']['total']])
        table.add_row(["  • Downloaded", summary['videos']['downloaded']])
        table.add_row(["  • Already existed", summary['videos']['already_exist']])
        table.add_row(["  • Skipped", summary['videos']['skipped']])
        table.add_row(["  • Failed", summary['videos']['failed']])
        
        # Add chapter summary
        table.add_row(["\nCHAPTERS", ""])
        table.add_row(["  • Total", summary['chapters']['total']])
        table.add_row(["  • Empty", summary['chapters']['empty']])
        table.add_row(["  • Deleted", summary['chapters']['deleted']])
        
        # Add errors if any
        if summary['errors']:
            table.add_row(["\nERRORS", ""])
            for i, error in enumerate(summary['errors'][:5], 1):
                table.add_row([f"  {i}. {error}", ""])
            if len(summary['errors']) > 5:
                table.add_row([f"  ... and {len(summary['errors']) - 5} more errors", ""])
        
        # Print the table
        click.echo("\n" + "=" * 80)
        click.echo(table.draw())
        click.echo("=" * 80)
        
        self._stop_spinner()
        
        # Print final status
        status = "✅ Download completed successfully!" if not summary['errors'] else "⚠️  Download completed with errors!"
        click.echo(click.style(f"\n{status}\n", fg="green" if not summary['errors'] else "yellow"))

    def _start_spinner(self, message):
        """Start a simple dot-based progress indicator"""
        sys.stdout.write(click.style(message, fg="cyan"))
        sys.stdout.flush()
        
    def _start_modified_spinner(self, message):
        """Print dots to show progress without cluttering the output"""
        sys.stdout.write(click.style(".", fg="cyan"))
        sys.stdout.flush()
        
    def _stop_spinner(self):
        """Ensure output ends with a newline"""
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _request_with_proxies(self, method, url, **kwargs):
        """
        Try all proxies in self.proxies for a request, return the first successful response.
        If no proxies or all fail, raise the last exception.
        """
        proxies = self.proxies if self.proxies else [None]
        last_exc = None
        for proxy in proxies:
            try:
                with Session() as session:
                    if proxy:
                        session.proxies = {"http": proxy, "https": proxy}
                    resp = session.request(method, url, **kwargs)
                    resp.raise_for_status()
                    return resp
            except Exception as exc:
                last_exc = exc
                continue
        raise last_exc if last_exc else Exception("All proxies failed or no proxies provided.")
