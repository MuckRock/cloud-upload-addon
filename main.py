""" We use clouddl, a library to grab files from several file sharing sites
and the DocumentCloud Add-On system"""
import os
import sys
from clouddl import grab
from documentcloud.addon import AddOn
from documentcloud.exceptions import APIError, DoesNotExistError


class Import(AddOn):
    """An Add-On that allows you to upload files into DocumentCloud from
    Google Drive & Dropbox"""

    def main(self):
        """
        Uses clouddl to grab documents from a Google Drive or Dropbox location,
        uploads them to DocumentCloud using upload_directory()
        """
        try:
            project = self.client.projects.get(self.data.get("project_id"))
        except DoesNotExistError:
            self.set_message("Invalid project ID specified. Try again")
            sys.exit(0)
        except APIError:
            self.set_message("Invalid project ID specified. Try again")
            sys.exit(0)
        os.makedirs(os.path.dirname("./out/"), exist_ok=True)
        url = self.data["url"]
        grab(url, "./out/")
        self.client.documents.upload_directory(
            "./out/",
            extensions=None,
            project=project.id,
            access=self.data.get("access_level"),
        )


if __name__ == "__main__":
    Import().main()
