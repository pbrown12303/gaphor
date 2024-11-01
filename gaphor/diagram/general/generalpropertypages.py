import base64
import io
from pathlib import Path

from PIL import Image

from gaphor.core import gettext
from gaphor.diagram.general.metadata import MetadataItem
from gaphor.diagram.general.picture import PictureItem
from gaphor.diagram.iconname import to_kebab_case
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_builder,
)
from gaphor.transaction import Transaction
from gaphor.ui.errorhandler import error_handler
from gaphor.ui.filedialog import open_file_dialog


@PropertyPages.register(MetadataItem)
class MetadataPropertyPage(PropertyPageBase):
    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager
        self.watcher = item and item.watcher()

    def construct(self):
        attrs = [
            "createdBy",
            "description",
            "website",
            "revision",
            "license",
            "createdOn",
            "updatedOn",
        ]

        builder = new_builder(
            "metadata-editor",
            signals={
                f"{to_kebab_case(a)}-changed": (self._on_field_change, a) for a in attrs
            },
        )

        item = self.item

        for a in attrs:
            builder.get_object(f"{to_kebab_case(a)}").set_text(getattr(item, a) or "")

        return builder.get_object("metadata-editor")

    def _on_field_change(self, entry, field_name):
        with Transaction(self.event_manager):
            text = entry.get_text()
            setattr(self.item, field_name, text)


@PropertyPages.register(PictureItem)
class PicturePropertyPage(PropertyPageBase):
    """Edit picture settings"""

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "picture-editor",
            signals={
                "select-picture": (self._on_select_picture_clicked,),
                "set-default-size": (self._on_default_size_clicked),
            },
        )
        return builder.get_object("picture-editor")

    def _on_select_picture_clicked(self, button):
        open_file_dialog(
            gettext("Select a picture..."),
            self.open_file,
            image_filter=True,
            parent=button.get_root(),
            multiple=False,
        )

    def open_file(self, filename):
        with open(filename, "rb") as file:
            try:
                image_data = file.read()
                with Image.open(io.BytesIO(image_data)) as image:
                    image.verify()

                    base64_encoded_data = base64.b64encode(image_data)

                    with Transaction(self.event_manager):
                        self.subject.subject.content = base64_encoded_data.decode(
                            "ascii"
                        )
                        self.subject.width = image.width
                        self.subject.height = image.height
                        if self.subject.subject.name in [
                            None,
                            gettext("New Picture"),
                        ] and (new_image_name := self.sanitize_image_name(filename)):
                            self.subject.subject.name = new_image_name
            except Exception:
                error_handler(
                    message=gettext("Unable to parse picture “{filename}”.").format(
                        filename=filename
                    )
                )

    def _on_default_size_clicked(self, button):
        if self.subject and self.subject.subject and self.subject.subject.content:
            base64_img_bytes = self.subject.subject.content.encode("ascii")
            image_data = base64.decodebytes(base64_img_bytes)
            image = Image.open(io.BytesIO(image_data))

            with Transaction(self.event_manager):
                self.subject.width = image.width
                self.subject.height = image.height

    def sanitize_image_name(self, filename):
        return "".join(
            chr if chr.isalnum() or (chr in [" ", "_", "-"]) else "_"
            for chr in Path(filename).stem
        )
