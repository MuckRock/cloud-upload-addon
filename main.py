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

        access = self.data.get("access_level")
        successes = 0
        errors = 0
        for path in grabbed:
            name = os.path.basename(path)
            _title, ext = os.path.splitext(name)
            ext = ext.lstrip(".").lower()
            if not ext:
                print(f"Skipping {path}: no file extension, can't determine type")
                errors += 1
                continue

            self.set_message(f"Uploading {name}...")
            print(f"Uploading {path} (original_extension={ext!r}, kwargs={kwargs!r})")
            try:
                doc = self.client.documents.upload(
                    path,
                    original_extension=ext,
                    access=access,
                    **kwargs,
                )
            except APIError as e:
                print(f"upload failed for {path}: {e}")
                errors += 1
                continue

            print(f"uploaded {path} -> pk {doc.id}")
            successes += 1

        sfiles = "file" if successes == 1 else "files"
        efiles = "file" if errors == 1 else "files"
        print(f"Done: {successes} uploaded, {errors} skipped/failed")
        self.set_message(f"Uploaded {successes} {sfiles}, skipped {errors} {efiles}")


if __name__ == "__main__":
    Import().main()
