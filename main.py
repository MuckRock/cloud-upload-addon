"""We use clouddl, a library to grab files from several file sharing sites
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

        me = self.client.users.get("me")
        print("client identity:", me.id, me.username)
        
        url = self.data["url"]
        project_id = self.data.get("project_id")

        kwargs = {}
        if project_id:
            try:
                project = self.client.projects.get(project_id)
                kwargs["project"] = project.id
                print(f"Resolved project {project_id} -> id {project.id}")
            except (DoesNotExistError, APIError) as e:
                print(f"Failed to resolve project_id={project_id!r}: {e}")
                self.set_message("Invalid project ID specified. Try again")
                sys.exit(0)
        else:
            print("No project_id supplied; uploading without a project")

        os.makedirs("./out/", exist_ok=True)

        print(f"Calling grab(url={url!r})")
        result = grab(url, "./out/")
        print(f"grab returned: {result!r}")

        grabbed = []
        for root, _dirs, files in os.walk("./out/"):
            for name in files:
                path = os.path.join(root, name)
                size = os.path.getsize(path)
                grabbed.append(path)
                print(f"grabbed file: {path} ({size} bytes)")

        print(f"Total files after grab: {len(grabbed)}")
        if not grabbed:
            print(f"Nothing downloaded from {url!r}")
            self.set_message("Couldn't download anything from that link.")
            sys.exit(0)

        print(f"Uploading {len(grabbed)} file(s) with kwargs={kwargs!r}")
        try:
            self.client.documents.upload_directory(
                "./out/",
                extensions=None,
                access=self.data.get("access_level"),
                **kwargs,
            )
        except APIError as e:
            print(f"upload_directory raised APIError: {e}")
            self.set_message("Upload failed — see logs.")
            sys.exit(1)

        print("upload_directory completed")
        self.set_message(f"Uploaded {len(grabbed)} file(s).")


if __name__ == "__main__":
    Import().main()
