"""
Запуск:
    python map_listings.py                       # обе карты (static + interactive)
    python map_listings.py --mode static
    python map_listings.py --mode interactive
    python map_listings.py --color-col rooms      # можно красить и по другой колонке
"""

import argparse
import os

import pandas as pd

CITY_NAME = "Архангельск"
CITY_CENTER = (64.5401, 40.5433)  # (lat, lon)
CITY_BBOX = {  # грубая рамка — отсекает координаты, реально не попавшие в город
    "min_lat": 64.40, "max_lat": 64.70,
    "min_lon": 40.30, "max_lon": 40.80,
}

CSV_PATH = "arhangelsk_rent_cleaned.csv"


# ---------------------------------------------------------------------------
# 1. Загрузка и подготовка данных
# ---------------------------------------------------------------------------
def load_offers(csv_path: str = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df = df.dropna(subset=["latitude", "longitude"]).copy()
    df = df[
        df["latitude"].between(CITY_BBOX["min_lat"], CITY_BBOX["max_lat"])
        & df["longitude"].between(CITY_BBOX["min_lon"], CITY_BBOX["max_lon"])
    ]

    # цена за м2 нужна для раскраски карты, в исходном файле её нет
    df["price_m2"] = (df["price_month"] / df["area_total"]).round(1)
    return df


# ---------------------------------------------------------------------------
# 2. DataFrame -> GeoDataFrame
# ---------------------------------------------------------------------------
def build_geodataframe(df: pd.DataFrame):
    import geopandas as gpd
    from shapely.geometry import Point

    geometry = [Point(lon, lat) for lat, lon in zip(df["latitude"], df["longitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")  # WGS84
    return gdf


# ---------------------------------------------------------------------------
# 3a. Статичная карта: geopandas + contextily (подложка OpenStreetMap)
# ---------------------------------------------------------------------------
def plot_static_map(
    gdf,
    out_path="charts/09_offers_map.png",
    color_col="price_m2",
    size_col="price_month",
):
    import matplotlib.pyplot as plt
    import contextily as cx

    gdf_web = gdf.to_crs(epsg=3857)  # проекция для тайлов Web Mercator

    fig, ax = plt.subplots(figsize=(9, 9))

    sizes = None
    if size_col in gdf_web.columns:
        s = gdf_web[size_col].astype(float)
        sizes = 20 + 180 * (s - s.min()) / (s.max() - s.min() + 1e-9)

    gdf_web.plot(
        ax=ax,
        column=color_col,
        cmap="viridis",
        markersize=sizes if sizes is not None else 40,
        alpha=0.85,
        edgecolor="white",
        linewidth=0.4,
        legend=True,
        legend_kwds={"label": color_col, "shrink": 0.6},
    )

    cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
    ax.set_axis_off()
    ax.set_title(f"Объявления об аренде — {CITY_NAME}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"saved -> {out_path}")


# ---------------------------------------------------------------------------
# 3b. Интерактивная карта: folium (HTML, открывается в браузере)
# ---------------------------------------------------------------------------
def plot_interactive_map(gdf, out_path="charts/09_offers_map.html", color_col="price_m2"):
    import folium
    from folium.plugins import MarkerCluster

    m = folium.Map(location=list(CITY_CENTER), zoom_start=12, tiles="CartoDB positron")
    cluster = MarkerCluster().add_to(m)

    vmin, vmax = gdf[color_col].min(), gdf[color_col].max()

    def color_for(value):
        ratio = 0 if vmax == vmin else (value - vmin) / (vmax - vmin)
        if ratio < 0.33:
            return "green"
        elif ratio < 0.66:
            return "orange"
        return "red"

    for _, row in gdf.iterrows():
        popup_html = (
            f"<b>{int(row['rooms'])}-комн., {row['area_total']:.0f} м²</b><br>"
            f"Цена: {row['price_month']:.0f} ₽/мес<br>"
            f"Цена за м²: {row['price_m2']:.0f}<br>"
            f"Этаж: {int(row['floor'])} из {int(row['floors_total'])}<br>"
            f"Год постройки: {int(row['building_year'])}<br>"
            f"<a href='{row['url']}' target='_blank'>Объявление</a>"
        )
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=6,
            color=color_for(row[color_col]),
            fill=True,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(cluster)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    m.save(out_path)
    print(f"saved -> {out_path} (откройте в браузере)")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Карта объявлений об аренде — Архангельск")
    parser.add_argument("--csv", default=CSV_PATH)
    parser.add_argument("--mode", choices=["static", "interactive", "both"], default="both")
    parser.add_argument("--color-col", default="price_m2")
    args = parser.parse_args()

    df = load_offers(args.csv)
    gdf = build_geodataframe(df)
    print(f"На карте будет {len(gdf)} из {len(pd.read_csv(args.csv))} объявлений (после фильтрации по границам города).")

    if args.mode in ("static", "both"):
        plot_static_map(gdf, color_col=args.color_col)
    if args.mode in ("interactive", "both"):
        plot_interactive_map(gdf, color_col=args.color_col)


if __name__ == "__main__":
    main()
