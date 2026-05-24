import streamlit as st
import requests
import json

# Функция получения данных
def get_bitcoin_price():
    try:
        # Получить данные о цене биткоина
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true')
        data = response.json()
        # Получить текущую цену и изменение за 24 часа
        current_price = data['bitcoin']['usd']
        price_change_percentage = data['bitcoin']['usd_24h_change']

        return current_price, price_change_percentage
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка получения данных: {e}")
        return None, None

# Инициализация приложения Streamlit
st.title('Курс биткоина в реальном времени')
st.subheader('Актуальная информация о цене биткоина и изменение за 24 часа')

# Добавить кнопку обновления
if st.button('Обновить курс'):
    st.experimental_rerun()

# Отобразить индикатор загрузки
with st.spinner('Загрузка...'):
    current_price, price_change_percentage = get_bitcoin_price()

# Отобразить данные
if current_price is not None:
    st.metric(label="Текущая цена биткоина (USD)", value=f"${current_price}")

    if price_change_percentage is not None:
        st.metric(label="Изменение за 24 часа (%)", value=f"{price_change_percentage:.2f}%")
else:
    st.error("Не удалось получить данные. Попробуйте позже.")
