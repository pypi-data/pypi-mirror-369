from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from ..exceptions import ValidationError
from .base import BaseEndpoint


class DV3FEndpoint(BaseEndpoint):
    """Endpoints DV3F (accès restreint): mutations + geomutations + mutation par id."""

    def mutations(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        anneemut: Optional[str] = None,
        anneemut_min: Optional[str] = None,
        anneemut_max: Optional[str] = None,
        codtypbien: Optional[str] = None,
        idnatmut: Optional[str] = None,
        vefa: Optional[str] = None,
        codtypproa: Optional[str] = None,
        codtypprov: Optional[str] = None,
        filtre: Optional[str] = None,
        segmtab: Optional[str] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,
                max_codes=10,
            )
        )
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            codtypproa=codtypproa,
            codtypprov=codtypprov,
            filtre=filtre,
            segmtab=segmtab,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
        return self._fetch(
            endpoint="/dv3f/mutations",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def geomutations(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        anneemut: Optional[str] = None,
        anneemut_min: Optional[str] = None,
        anneemut_max: Optional[str] = None,
        codtypbien: Optional[str] = None,
        idnatmut: Optional[str] = None,
        vefa: Optional[str] = None,
        codtypproa: Optional[str] = None,
        codtypprov: Optional[str] = None,
        filtre: Optional[str] = None,
        segmtab: Optional[str] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,
                max_codes=10,
            )
        )
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            codtypproa=codtypproa,
            codtypprov=codtypprov,
            filtre=filtre,
            segmtab=segmtab,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            page=page,
            page_size=page_size,
        )
        return self._fetch(
            endpoint="/dv3f/geomutations",
            params=params,
            format_output=format_output,
            geo=True,
            paginate=paginate,
        )

    def mutation_by_id(
        self,
        idmutation: int,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        if idmutation is None:
            raise ValidationError("idmutation est obligatoire")
        return self._fetch(
            endpoint=f"/dv3f/mutations/{idmutation}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )
