"""
AnnotatableXBlock allows instructors to add interactive annotations to course content.
Annotations can have configurable attributes such as title, body, problem index, and highlight color.
This block enhances the learning experience by enabling students to view embedded comments, questions, or explanations.
The block supports internationalization (i18n) for multilingual courses.
"""

import logging
import textwrap
import uuid

import markupsafe
from django.utils.translation import gettext_noop as _
from lxml import etree
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String, XMLString
from xblock.utils.resources import ResourceLoader

log = logging.getLogger(__name__)

resource_loader = ResourceLoader(__name__)


@XBlock.needs("i18n")
class AnnotatableBlock(XBlock):
    """
    AnnotatableXBlock allows instructors to create annotated content that students can view interactively.
    Annotations can be styled and customized, with internationalization support for multilingual environments.
    """

    # Indicates that this XBlock has been extracted from edx-platform.
    is_extracted = True

    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        scope=Scope.settings,
        default=_("Annotation"),
    )

    data = XMLString(
        help=_("XML data for the annotation"),
        scope=Scope.content,
        default=textwrap.dedent(
            markupsafe.Markup(
                """
                <annotatable>
                    <instructions>
                        <p>Enter your (optional) instructions for the exercise in HTML format.</p>
                        <p>Annotations are specified by an <code>{}annotation{}</code> tag which may
                        may have the following attributes:</p>
                        <ul class="instructions-template">
                            <li><code>title</code> (optional). Title of the annotation. Defaults to
                            <i>Commentary</i> if omitted.</li>
                            <li><code>body</code> (<b>required</b>). Text of the annotation.</li>
                            <li><code>problem</code> (optional). Numeric index of the problem
                            associated with this annotation. This is a zero-based index, so the first
                            problem on the page would have <code>problem="0"</code>.</li>
                            <li><code>highlight</code> (optional). Possible values: yellow, red,
                            orange, green, blue, or purple. Defaults to yellow if this attribute is
                            omitted.</li>
                        </ul>
                    </instructions>
                    <p>Add your HTML with annotation spans here.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    <annotation title="My title" body="My comment" highlight="yellow" problem="0">
                    Ut sodales laoreet est, egestas gravida felis egestas nec.</annotation> Aenean
                    at volutpat erat. Cras commodo viverra nibh in aliquam.</p>
                    <p>Nulla facilisi. <annotation body="Basic annotation example." problem="1">
                    Pellentesque id vestibulum libero.</annotation> Suspendisse potenti. Morbi
                    scelerisque nisi vitae felis dictum mattis. Nam sit amet magna elit. Nullam
                    volutpat cursus est, sit amet sagittis odio vulputate et. Curabitur euismod, orci
                    in vulputate imperdiet, augue lorem tempor purus, id aliquet augue turpis a est.
                    Aenean a sagittis libero. Praesent fringilla pretium magna, non condimentum risus
                    elementum nec. Pellentesque faucibus elementum pharetra. Pellentesque vitae metus
                    eros.</p>
                </annotatable>
                """
            ).format(markupsafe.escape("<"), markupsafe.escape(">"))
        ),
    )

    # List of supported highlight colors for annotations
    HIGHLIGHT_COLORS = ["yellow", "orange", "purple", "blue", "green"]

    def _get_annotation_class_attr(self, index, el):  # pylint: disable=unused-argument
        """Returns a dict with the CSS class attribute to set on the annotation
        and an XML key to delete from the element.
        """

        attr = {}
        cls = ["annotatable-span", "highlight"]
        highlight_key = "highlight"
        color = el.get(highlight_key)

        if color is not None:
            if color in self.HIGHLIGHT_COLORS:
                cls.append("highlight-" + color)
            attr["_delete"] = highlight_key
        attr["value"] = " ".join(cls)

        return {"class": attr}

    def _get_annotation_data_attr(self, index, el):  # pylint: disable=unused-argument
        """Returns a dict in which the keys are the HTML data attributes
        to set on the annotation element. Each data attribute has a
        corresponding 'value' and (optional) '_delete' key to specify
        an XML attribute to delete.
        """

        data_attrs = {}
        attrs_map = {
            "body": "data-comment-body",
            "title": "data-comment-title",
            "problem": "data-problem-id",
        }

        for xml_key, html_key in attrs_map.items():
            if xml_key in el.attrib:
                value = el.get(xml_key, "")
                data_attrs[html_key] = {"value": value, "_delete": xml_key}

        return data_attrs

    def _render_annotation(self, index, el):
        """Renders an annotation element for HTML output."""
        attr = {}
        attr.update(self._get_annotation_class_attr(index, el))
        attr.update(self._get_annotation_data_attr(index, el))

        el.tag = "span"

        for key, value in attr.items():
            el.set(key, value["value"])
            if "_delete" in value and value["_delete"] is not None:
                delete_key = value["_delete"]
                del el.attrib[delete_key]

    def _render_content(self):
        """Renders annotatable content with annotation spans and returns HTML."""

        xmltree = etree.fromstring(self.data)
        self._extract_instructions(xmltree)

        xmltree.tag = "div"
        if "display_name" in xmltree.attrib:
            del xmltree.attrib["display_name"]

        index = 0
        for el in xmltree.findall(".//annotation"):
            self._render_annotation(index, el)
            index += 1

        return etree.tostring(xmltree, encoding="unicode")

    def _extract_instructions(self, xmltree):
        """Removes <instructions> from the xmltree and returns them as a string, otherwise None."""
        instructions = xmltree.find("instructions")
        if instructions is not None:
            instructions.tag = "div"
            xmltree.remove(instructions)
            return etree.tostring(instructions, encoding="unicode")
        return None

    def get_html(self):
        """Returns the HTML representation of the XBlock for student view."""
        return {
            "element_id": uuid.uuid1(0),
            "display_name": self.display_name,
            "instructions_html": self._extract_instructions(etree.fromstring(self.data)),
            "content_html": self._render_content(),
        }

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """Renders the output that a student will see."""
        frag = Fragment()
        frag.add_content(
            resource_loader.render_django_template(
                "templates/annotatable.html",
                self.get_html(),
                i18n_service=self.runtime.service(self, "i18n"),
            )
        )
        frag.add_css(resource_loader.load_unicode("static/css/annotatable.css"))
        frag.add_javascript(resource_loader.load_unicode("static/js/src/annotatable.js"))
        frag.initialize_js("Annotatable")
        return frag

    def studio_view(self, context=None):  # pylint: disable=unused-argument
        """Return the studio view."""
        frag = Fragment()
        frag.add_content(
            resource_loader.render_django_template(
                "templates/annotatable_editor.html",
                {
                    "data": self.data,
                },
                i18n_service=self.runtime.service(self, "i18n"),
            )
        )

        frag.add_css(resource_loader.load_unicode("static/css/annotatable_editor.css"))
        frag.add_javascript(resource_loader.load_unicode("static/js/src/annotatable_editor.js"))
        frag.initialize_js("XMLEditingDescriptor")
        return frag

    @XBlock.json_handler
    def submit_studio_edits(self, data, suffix=""):  # pylint: disable=unused-argument
        """AJAX handler for saving the studio edits."""
        display_name = data.get("display_name")
        xml_data = data.get("data")

        if display_name is not None:
            self.display_name = display_name
        if xml_data is not None:
            self.data = xml_data

        return {"result": "success"}

    @staticmethod
    def workbench_scenarios():
        """Defines scenarios for displaying the XBlock in the XBlock workbench."""
        return [
            ("AnnotatableXBlock", "<_annotatable_extracted/>"),
            (
                "Multiple AnnotatableXBlock",
                """
                <vertical_demo>
                    <_annotatable_extracted/>
                    <_annotatable_extracted/>
                    <_annotatable_extracted/>
                </vertical_demo>
            """,
            ),
        ]
