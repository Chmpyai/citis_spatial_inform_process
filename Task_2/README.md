# Задание 2 — растяжение уровней RGB

Команды ниже выполняются в PowerShell из корня репозитория `citis_spatial_inform_process`. Python-окружение должно содержать `numpy` и `matplotlib`.

## Запуск Python

```powershell
conda activate def_conda_env
python .\Task_2\code\generate_data.py
python .\Task_2\code\process_python.py
```

`generate_data.py` создаёт общий набор из 500 точек в `Task_2\code\data\source.txt`. `process_python.py` обрабатывает RGB, сохраняет Python-результат и строит графики в `Task_2\code\output`.

## CloudCompare и сравнение

1. Откройте в CloudCompare `Task_2\code\data\source.txt`.
2. Для облака выберите **Edit → Colors → Levels**. Установите канал **RGB**, вход `60–160`, выход `0–255` и нажмите **Apply**.
3. Экспортируйте ASCII в `Task_2\code\output\result_cloudcompare.txt`, сохранив координаты, RGB и ID в порядке `X Y Z R G B ID`; RGB — целыми числами `0–255`.
4. Из корня репозитория запустите сравнение:

```powershell
python .\Task_2\code\compare_results.py
```

Отчёт сравнения появится в `Task_2\code\output\comparison.txt`.

## Файлы и результаты

- `Task_2\code` содержит скрипты, исходные данные и результаты. Файлы задания `task.txt` и `task.pdf` лежат рядом с этим README.
- `Task_2\slides` содержит готовую презентацию в форматах PDF/PPTX и текст выступления.
- Обработано `500` точек; ID совпали.
- Максимальное расхождение XYZ: `4.8 × 10⁻⁷ м`.
- Максимальное расхождение RGB: `1` уровень; допуск `≤1` выполнен. На `698` из `1500` компонент разница ровно 1.
