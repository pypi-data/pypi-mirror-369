from __future__ import annotations
from typing import (
    Literal,
    Optional,
    Union,
)
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.vars.js_computed import JsComputed
from instaui.components.element import Element
from .base_props import TLayoutBaseProps
from instaui.components._responsive_type._common import TMaybeResponsive, TLevel_0_9
from instaui.components._responsive_utils import gen_responsive_props


class Grid(Element):
    def __init__(
        self,
        *,
        as_: Optional[TMaybeRef[Literal["div", "span"]]] = None,
        as_child: Optional[TMaybeRef[bool]] = None,
        display: Optional[
            TMaybeResponsive[Literal["none", "inline-grid", "grid"]]
        ] = None,
        areas: Optional[TMaybeResponsive[str]] = None,
        columns: Optional[TMaybeResponsive[Union[int, str, TLevel_0_9]]] = None,
        rows: Optional[TMaybeResponsive[Union[int, str, TLevel_0_9]]] = None,
        flow: Optional[
            TMaybeResponsive[Literal["row", "column", "row-dense", "column-dense"]]
        ] = None,
        align: Optional[
            TMaybeResponsive[Literal["start", "center", "end", "baseline", "stretch"]]
        ] = None,
        justify: Optional[
            TMaybeResponsive[Literal["start", "center", "end", "between"]]
        ] = None,
        gap: Optional[TMaybeResponsive[Union[str, TLevel_0_9]]] = None,
        gap_x: Optional[TMaybeResponsive[Union[str, TLevel_0_9]]] = None,
        gap_y: Optional[TMaybeResponsive[Union[str, TLevel_0_9]]] = None,
        **kwargs: Unpack[TLayoutBaseProps],
    ):
        '''Grid component

        Args:
            rows (Optional[TMaybeRef[Union[int, str]]], optional): Number of rows or template for rows. Defaults to None.
            columns (Optional[TMaybeRef[Union[int, str]]], optional): Number of columns or template for columns. Defaults to None.

        # Example:
        columns example:
        .. code-block:: python
            border = "border-2 border-gray-200"

            with ui.grid(columns=2, h='200px').classes(border) as g:

                # a in the first row and first column
                html.paragraph("a value").classes(border)
                # b in the first row and second column
                html.paragraph("b value").classes(border)

                # c in the second row and span over 2 columns
                html.paragraph("c value").use(
                    g.mark_area_position(column_span=2)
                ).classes(border)

        template areas example:
        .. code-block:: python
            border = "border-2 border-gray-200"

            template = r"""
            "a b c"
            "a b ."
            """

            with ui.grid(areas=template, h='200px').classes(border) as g:
                html.paragraph("a value").use(g.mark_area("a")).classes(border)
                html.paragraph("b value").use(g.mark_area("b")).classes(border)
                html.paragraph("c value").use(g.mark_area("c")).classes(border)
        '''

        super().__init__("grid")

        self.props(
            gen_responsive_props(
                {
                    "as": as_,
                    "as_child": as_child,
                    "display": display,
                    "areas": areas,
                    "columns": columns,
                    "rows": rows,
                    "flow": flow,
                    "align": align,
                    "justify": justify,
                    "gap": gap,
                    "gap_x": gap_x,
                    "gap_y": gap_y,
                    **kwargs,
                }
            )
        )

    def mark_area(self, area: TMaybeRef[str]):
        """Marks an area in the grid

        Args:
            area (TMaybeRef[str]): Area name

        """

        def use_fn(element: Element):
            element.style({"grid-area": area})

        return use_fn

    def mark_area_position(
        self,
        *,
        row: Optional[int] = None,
        column: Optional[int] = None,
        row_span: Optional[int] = None,
        column_span: Optional[int] = None,
    ):
        """Marks an area in the grid with position

        Args:
            row (Optional[int], optional): Start position of row, 1-based. Defaults to None.
            column (Optional[int], optional): Start position of column, 1-based. Defaults to None.
            row_span (Optional[int], optional): The span value at the end of the row. Defaults to None.
            column_span (Optional[int], optional): The span value at the end of the column. Defaults to None.
        """
        real_row = "auto" if row is None else row
        real_column = "auto" if column is None else column
        real_row_span = "auto" if row_span is None else f"span {row_span}"
        real_column_span = "auto" if column_span is None else f"span {column_span}"

        area = f"{real_row} / {real_column} / {real_row_span} / {real_column_span}"
        return self.mark_area(area)

    @staticmethod
    def auto_columns(
        *,
        min_width: TMaybeRef[str],
        mode: TMaybeRef[Literal["auto-fill", "auto-fit"]] = "auto-fit",
    ):
        """
        Generate a dynamic grid column configuration for responsive layout systems.

        Creates a computed layout specification that calculates column dimensions
        based on minimum width requirements and auto-sizing behavior. Retu

        Args:
            min_width (TMaybeRef[str]):
                Minimum width constraint for columns as a CSS length string (e.g., "300px").
                Accepts reactive references for dynamic updates.
            mode (TMaybeRef[Literal[&quot;auto, optional):
                Auto-sizing behavior strategy:
                - "auto-fill": Preserves container space by creating additional columns
                - "auto-fit": Adjusts columns to fit available space.
                Defaults to "auto-fit".

        Example:
        .. code-block:: python

            with ui.grid(columns=ui.grid.auto_columns(min_width="300px")):
                ...
        """
        template = JsComputed(
            inputs=[min_width, mode],
            code=r"(min_width, mode)=> `repeat(${mode}, minmax(min(${min_width},100%), 1fr))`",
        )

        return template

    @staticmethod
    def auto_rows(
        *,
        min_height: TMaybeRef[str],
        mode: TMaybeRef[Literal["auto-fill", "auto-fit"]] = "auto-fit",
    ):
        """
        Generate a dynamic grid row configuration for responsive layout systems.

        Creates a computed layout specification that calculates row dimensions
        based on minimum height requirements and auto-sizing behavior.

        Args:
            min_height (TMaybeRef[str]):
                Minimum height constraint for rows as a CSS length string (e.g., "300px").
            mode (TMaybeRef[Literal[&quot;auto, optional):
                Auto-sizing behavior strategy:
                - "auto-fill": Preserves container space by creating additional rows
                - "auto-fit": Adjusts rows to fit available space.
                Defaults to "auto-fit".

        Example:
        .. code-block:: python

            with ui.grid(rows=ui.grid.auto_rows(min_height="300px")):
                ...
        """

        template = JsComputed(
            inputs=[min_height, mode],
            code=r"(min_height, mode)=> `repeat(${mode}, minmax(min(${min_height},100%), 1fr))`",
        )

        return template
