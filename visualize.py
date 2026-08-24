
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DATA_DIR = "results_script"
OUT_DIR = "charts"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
plt.rcParams["axes.axisbelow"] = True

COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"saved -> {path}")


# ---------------------------------------------------------------------------
# 1. Доля площади кухни / жилой площади в общей площади квартиры, по комнатности
# файл: _select_a_rooms_round_AVG_a_area_kitchen_a_area_total_2_as_avg_k_*.csv
# ---------------------------------------------------------------------------
def chart_kitchen_living_share():
    df = pd.read_csv(os.path.join(
        DATA_DIR,
        "_select_a_rooms_round_AVG_a_area_kitchen_a_area_total_2_as_avg_k_202608241221.csv",
    ))
    df = df.sort_values("rooms")

    x = df["rooms"].astype(str)
    width = 0.35
    positions = range(len(x))

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([p - width / 2 for p in positions], df["avg_kitchen_rate"], width,
           label="Доля кухни (avg)", color=COLORS[0])
    ax.bar([p + width / 2 for p in positions], df["avg_living_rate"], width,
           label="Доля жилой площади (avg)", color=COLORS[1])

    ax.set_xticks(list(positions))
    ax.set_xticklabels(x)
    ax.set_xlabel("Число комнат")
    ax.set_ylabel("Доля от общей площади")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_title("Доля площади кухни и жилой площади по числу комнат")
    ax.legend()
    save(fig, "01_kitchen_living_share_by_rooms.png")


# ---------------------------------------------------------------------------
# 2. Распределение предложений и медианной цены по числу комнат
# файлы: _select_rooms_count_as_offers_count_*.csv  и room_stat.csv (дубликат)
# ---------------------------------------------------------------------------
def chart_rooms_distribution(src_file, out_name, title_suffix=""):
    df = pd.read_csv(os.path.join(DATA_DIR, src_file)).sort_values("rooms")
    x = df["rooms"].astype(str)

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.bar(x, df["offers_count"], color=COLORS[0], alpha=0.8, label="Кол-во предложений")
    ax1.set_xlabel("Число комнат")
    ax1.set_ylabel("Количество предложений", color=COLORS[0])
    ax1.tick_params(axis="y", labelcolor=COLORS[0])

    ax2 = ax1.twinx()
    ax2.plot(x, df["price_median"], color=COLORS[3], marker="o", linewidth=2,
              label="Медианная цена, руб/мес")
    ax2.set_ylabel("Медианная цена, руб/мес", color=COLORS[3])
    ax2.tick_params(axis="y", labelcolor=COLORS[3])
    ax2.grid(False)

    fig.suptitle(f"Число предложений и медианная цена по комнатности{title_suffix}")
    save(fig, out_name)


# ---------------------------------------------------------------------------
# 3. Медианная цена за м2 по расположению этажа (первый/последний/средний)
# файл: _with_floor_segment_as_..._202608241224.csv
# ---------------------------------------------------------------------------
def chart_floor_segment_price():
    df = pd.read_csv(os.path.join(
        DATA_DIR, "_with_floor_segment_as_select_case_when_floor_floors_total_then__202608241224.csv"
    ))
    order = ["First_floor", "Mid_floor", "Last_floor"]
    df["category"] = pd.Categorical(df["category"], categories=order, ordered=True)
    df = df.sort_values("category")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(df["category"], df["price_m2_median"], color=COLORS[:3])
    ax.set_ylabel("Медианная цена за м², руб.")
    ax.set_xlabel("Расположение этажа")
    ax.set_title("Цена за м² в зависимости от расположения этажа")
    for b, v, n in zip(bars, df["price_m2_median"], df["count_offers"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.0f}\n(n={n})",
                ha="center", va="bottom", fontsize=9)
    save(fig, "03_price_by_floor_segment.png")


# ---------------------------------------------------------------------------
# 4. Средняя цена аренды и цена за м2 по ценовому сегменту (tile)
# файл: _with_price_metr_as_..._202608241224.csv
# ---------------------------------------------------------------------------
def chart_price_tile():
    df = pd.read_csv(os.path.join(
        DATA_DIR, "_with_price_metr_as_select_price_month_area_total_as_price_m2_ar_202608241224.csv"
    ))
    order = ["Economy", "Standard", "Comfort", "Premium"]
    df["tile"] = pd.Categorical(df["tile"], categories=order, ordered=True)
    df = df.sort_values("tile")

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    x = range(len(df))
    ax1.bar(x, df["avg_price_month"], color=COLORS[0], alpha=0.85)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["tile"])
    ax1.set_ylabel("Средняя цена аренды, руб/мес", color=COLORS[0])
    ax1.tick_params(axis="y", labelcolor=COLORS[0])
    ax1.set_xlabel("Ценовой сегмент")

    ax2 = ax1.twinx()
    ax2.plot(x, df["avg_price_m2"], color=COLORS[3], marker="o", linewidth=2)
    ax2.set_ylabel("Средняя цена за м², руб.", color=COLORS[3])
    ax2.tick_params(axis="y", labelcolor=COLORS[3])
    ax2.grid(False)

    ax1.set_title("Средняя цена аренды и цена за м² по ценовым сегментам")
    save(fig, "04_price_by_tile_segment.png")


# ---------------------------------------------------------------------------
# 5. Цена за м2 по возрасту дома (Historical / Soviet / Post-Soviet / Modern)
# файл: _with_t1_as_select_case_when_building_year_1960_then_Historical__*.csv
# ---------------------------------------------------------------------------
def chart_building_era():
    df = pd.read_csv(os.path.join(
        DATA_DIR, "_with_t1_as_select_case_when_building_year_1960_then_Historical__202608241223.csv"
    ))
    order = ["Historical", "Soviet", "Post-Soviet", "Modern"]
    df["category"] = pd.Categorical(df["category"], categories=order, ordered=True)
    df = df.sort_values("category")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(df["category"], df["median_price_m2"], color=COLORS[4])
    ax.set_ylabel("Медианная цена за м², руб.")
    ax.set_xlabel("Категория дома по году постройки")
    ax.set_title("Цена за м² в зависимости от возраста дома")
    for b, v, n in zip(bars, df["median_price_m2"], df["count_offers"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.0f}\n(n={n})",
                ha="center", va="bottom", fontsize=9)
    save(fig, "05_price_by_building_era.png")


# ---------------------------------------------------------------------------
# 6. Разброс цены за м2 по числу комнат + отклонение цены от средней (rank_by_price.csv)
# ---------------------------------------------------------------------------
def chart_rank_by_price():
    df = pd.read_csv(os.path.join(DATA_DIR, "rank_by_price.csv"))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 6a. Boxplot цены за м2 по комнатности
    groups = [df.loc[df["rooms"] == r, "price_m2"].values for r in sorted(df["rooms"].unique())]
    axes[0].boxplot(groups, labels=sorted(df["rooms"].unique()), showmeans=True)
    axes[0].set_xlabel("Число комнат")
    axes[0].set_ylabel("Цена за м², руб.")
    axes[0].set_title("Разброс цены за м² по комнатности")

    # 6b. Scatter: отклонение цены за м2 vs отклонение цены за мес (по рангу)
    scatter = axes[1].scatter(
        df["price_m2_deviation"], df["price_month_deviation"],
        c=df["rooms"], cmap="viridis", alpha=0.7, s=25
    )
    axes[1].axhline(0, color="gray", linewidth=0.8)
    axes[1].axvline(0, color="gray", linewidth=0.8)
    axes[1].set_xlabel("Отклонение цены за м² от средней по комнатности, %")
    axes[1].set_ylabel("Отклонение цены за мес. от средней по комнатности, %")
    axes[1].set_title("Переплата/недоплата относительно средней по комнатности")
    cbar = fig.colorbar(scatter, ax=axes[1])
    cbar.set_label("Число комнат")

    fig.suptitle("Ранжирование предложений по цене (rank_by_price)")
    save(fig, "06_rank_by_price.png")


# ---------------------------------------------------------------------------
# 7. Доля предложений по комнатности (room_stat.csv — дублирует данные из п.2)
# ---------------------------------------------------------------------------
def chart_room_stat_share():
    df = pd.read_csv(os.path.join(DATA_DIR, "room_stat.csv")).sort_values("rooms")

    fig, ax = plt.subplots(figsize=(6, 6))
    labels = [f"{r} комн." for r in df["rooms"]]
    ax.pie(
        df["offers_share"], labels=labels, autopct="%1.1f%%",
        colors=COLORS[: len(df)], startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    ax.set_title("Доля предложений по числу комнат (room_stat)")
    save(fig, "07_room_share_pie.png")


# ---------------------------------------------------------------------------
# 8. Изменение цены за м2 в зависимости от расположения этажа (t1.csv)
# ---------------------------------------------------------------------------
def chart_floor_price_change():
    df = pd.read_csv(os.path.join(DATA_DIR, "t1_202608241224.csv"))
    order = ["First_floor", "Mid_floor", "Last_floor"]
    df["category"] = pd.Categorical(df["category"], categories=order, ordered=True)
    df = df.sort_values("category")

    colors = [COLORS[3] if v < 0 else COLORS[2] for v in df["price_m2_change"]]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(df["category"], df["price_m2_change"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Отклонение цены за м² от среднего этажа, %")
    ax.set_xlabel("Расположение этажа")
    ax.set_title("Отклонение цены за м² относительно среднего этажа")
    for b, v in zip(bars, df["price_m2_change"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:+.2f}%",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=9)
    save(fig, "08_floor_price_change.png")


if __name__ == "__main__":
    chart_kitchen_living_share()
    chart_rooms_distribution(
        "_select_rooms_count_as_offers_count_count_numeric_SUM_COUNT_OVER_202608241223.csv",
        "02_offers_and_price_by_rooms.png",
    )
    chart_floor_segment_price()
    chart_price_tile()
    chart_building_era()
    chart_rank_by_price()
    chart_room_stat_share()
    chart_floor_price_change()
    print("\nВсе графики сохранены в папку charts/")
