from tkinter import Tk, filedialog
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import CheckButtons, Button
from scipy.signal import find_peaks


def load_data():
    print("Выберите Csv файл с данными")
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("Файл не выбран. Завершение.")
        exit()

    first_row = pd.read_csv(file_path, delimiter=',', nrows=1, header=None)
    temperatures = first_row.iloc[0, 1:].values

    data = pd.read_csv(file_path, delimiter=',', skiprows=1, header=None)
    x = pd.to_numeric(data.iloc[:, 0], errors='coerce')
    ys = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

    valid_mask = ~x.isna()
    x = x[valid_mask].values
    ys = ys[valid_mask].values

    x_energy = 1239.841984 / x
    y_correction = (1239.841984 / x_energy**2)
    ys = ys * y_correction[:, np.newaxis]

    return x_energy, ys, temperatures


def save_results(df):
    root = Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Сохранить результаты как")
    if file_path:
        df.to_csv(file_path, index=False)
        print(f"Результаты сохранены в {file_path}")


def show_found_peaks(x, ys, center, delta, i):
    fig_peaks, ax_peaks = plt.subplots()
    ax_peaks.set_title(f'Обнаруженные пики для Пика {i+1}')
    ax_peaks.set_xlabel('Энергия (эВ)')
    ax_peaks.set_ylabel('Интенсивность')

    for j, spectrum in enumerate(ys.T):
        y = spectrum
        y = y - np.min(y)
        mask = (x >= center - delta) & (x <= center + delta)
        x_sub = x[mask]
        y_sub = y[mask]

        ax_peaks.plot(x, y, alpha=0.3)

        peaks, _ = find_peaks(y_sub)
        if len(peaks) > 0:
            best = peaks[np.argmax(y_sub[peaks])]
            peak_x = x_sub[best]
            peak_y = y_sub[best]
            ax_peaks.plot(peak_x, peak_y, 'x', color=f'C{i}', markersize=8)

    plt.tight_layout()
    plt.show()


def show_opened_file(x, ys, temperatures_all):
    n_cols = 3
    n_rows = int(np.ceil(len(temperatures_all) / n_cols))

    fig_select, axs_select = plt.subplots(1, n_cols, figsize=(n_cols * 4, n_rows * 0.6))
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.2)

    if n_cols == 1:
        axs_select = [axs_select]

    labels = [str(temp) for temp in temperatures_all]
    visibility = [True] * len(labels)

    checks = []
    for i, ax in enumerate(axs_select):
        subset_labels = labels[i * n_rows:(i + 1) * n_rows]
        subset_visibility = visibility[i * n_rows:(i + 1) * n_rows]
        check = CheckButtons(ax, subset_labels, subset_visibility)
        checks.append(check)

    selected_indices = list(range(len(temperatures_all)))

    def update_selection(label):
        nonlocal selected_indices
        visibility_state = []
        for chk in checks:
            visibility_state.extend(chk.get_status())
        selected_indices = [i for i, v in enumerate(visibility_state) if v]

    for chk in checks:
        chk.on_clicked(update_selection)

    ax_button_all = plt.axes([0.3, 0.05, 0.15, 0.075])
    ax_button_none = plt.axes([0.5, 0.05, 0.15, 0.075])
    button_all = Button(ax_button_all, 'Выбрать все')
    button_none = Button(ax_button_none, 'Снять все')

    def select_all(event):
        for chk in checks:
            for i in range(len(chk.labels)):
                chk.set_active(i)

    def deselect_all(event):
        for chk in checks:
            for i in range(len(chk.labels)):
                if chk.get_status()[i]:
                    chk.set_active(i)

    button_all.on_clicked(select_all)
    button_none.on_clicked(deselect_all)

    plt.show()

    temperatures = temperatures_all[selected_indices]
    ys = ys[:, selected_indices]

    return x, ys, temperatures
