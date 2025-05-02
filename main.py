import pandas as pd

from utils import load_data, show_opened_file
from integration import run_peak_integration
from fwhm import run_fwhm_analysis
from peakpostions import run_peak_positions

# Загрузка CSV файла через диалоговое окно


# Выбор режима
def choose_mode():
    print("Выберите режим работы:")
    print("1 — Интеграл пиков от температуры")
    print("2 — Положение пиков от температуры")
    print("3 — Ширина пиков на полувысоте (FWHM)")
    return input("Введите номер режима: ").strip()


# Основная функция
def main():
    temp_x, temp_y, temp_t = load_data()
    x, ys, temperatures_raw = show_opened_file(temp_x, temp_y, temp_t)
    mode = choose_mode()
    temperatures_all = pd.to_numeric(pd.Series(temperatures_raw), errors='coerce').dropna().values

    if mode == '1':
        run_peak_integration(x, ys, temperatures_all)
    elif mode == '2':
        run_peak_positions(x, ys, temperatures_all)
    elif mode == '3':
        run_fwhm_analysis(x, ys, temperatures_all)
    else:
        print("Неверный выбор режима. Завершение.")

if __name__ == "__main__":
    main()
