<template>
  <div class="result-container">
    <!-- Заголовок страницы -->
    <div class="page-header">
      <a-button class="back-button" size="large" @click="goBack">
        ← На главную
      </a-button>
      <a-space size="middle">
        <a-button v-if="!editMode" @click="toggleEditMode" type="default">
          ✏️ Редактировать маршрут
        </a-button>
        <a-button v-else @click="saveChanges" type="primary">
          💾 Сохранить изменения
        </a-button>
        <a-button v-if="editMode" @click="cancelEdit" type="default">
          ❌ Отменить редактирование
        </a-button>

        <!-- Кнопки экспорта -->
        <a-dropdown v-if="!editMode">
          <template #overlay>
            <a-menu>
              <a-menu-item key="image" @click="exportAsImage">
                📷 Экспортировать как изображение
              </a-menu-item>
              <a-menu-item key="pdf" @click="exportAsPDF">
                📄 Экспортировать в PDF
              </a-menu-item>
            </a-menu>
          </template>
          <a-button type="default">
            📥 Экспортировать маршрут <DownOutlined />
          </a-button>
        </a-dropdown>
      </a-space>
    </div>

    <div v-if="tripPlan" class="content-wrapper">
      <!-- Боковая навигация -->
      <div class="side-nav">
        <a-affix :offset-top="80">
          <a-menu mode="inline" :selected-keys="[activeSection]" @click="scrollToSection">
            <a-menu-item key="overview">
              <span>📋 Обзор маршрута</span>
            </a-menu-item>
            <a-menu-item key="budget" v-if="tripPlan.budget">
              <span>💰 Детали бюджета</span>
            </a-menu-item>
            <a-menu-item key="map">
              <span>📍 Карта достопримечательностей</span>
            </a-menu-item>
            <a-sub-menu key="days" title="📅 Ежедневный маршрут">
              <a-menu-item v-for="(day, index) in tripPlan.days" :key="`day-${index}`">
                День {{ day.day_index + 1 }}
              </a-menu-item>
            </a-sub-menu>
            <a-menu-item key="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0">
              <span>🌤️ Погода</span>
            </a-menu-item>
          </a-menu>
        </a-affix>
      </div>

      <!-- Основная область контента -->
      <div class="main-content">
        <!-- Верхний блок: слева — обзор и бюджет, справа — карта -->
        <div class="top-info-section">
          <!-- Левый блок: обзор маршрута и детали бюджета -->
          <div class="left-info">
            <!-- Обзор маршрута -->
            <a-card id="overview" :title="`План путешествия по ${tripPlan.city}`" :bordered="false" class="overview-card">
              <div class="overview-content">
                <div class="info-item">
                  <span class="info-label">📅 Даты:</span>
                  <span class="info-value">{{ tripPlan.start_date }} — {{ tripPlan.end_date }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">💡 Рекомендации:</span>
                  <span class="info-value">{{ tripPlan.overall_suggestions }}</span>
                </div>
              </div>
            </a-card>

            <!-- Детали бюджета -->
            <a-card id="budget" v-if="tripPlan.budget" title="💰 Детали бюджета" :bordered="false" class="budget-card">
              <div class="budget-grid">
                <div class="budget-item">
                  <div class="budget-label">Билеты</div>
                  <div class="budget-value">{{ tripPlan.budget.total_attractions }} руб.</div>
                </div>
                <div class="budget-item">
                  <div class="budget-label">Проживание</div>
                  <div class="budget-value">{{ tripPlan.budget.total_hotels }} руб.</div>
                </div>
                <div class="budget-item">
                  <div class="budget-label">Питание</div>
                  <div class="budget-value">{{ tripPlan.budget.total_meals }} руб.</div>
                </div>
                <div class="budget-item">
                  <div class="budget-label">Транспорт</div>
                  <div class="budget-value">{{ tripPlan.budget.total_transportation }} руб.</div>
                </div>
              </div>
              <div class="budget-total">
                <span class="total-label">Ориентировочный итог</span>
                <span class="total-value">{{ tripPlan.budget.total }} руб.</span>
              </div>
            </a-card>
          </div>

          <!-- Правый блок: карта -->
          <div class="right-map">
            <a-card id="map" title="📍 Карта достопримечательностей" :bordered="false" class="map-card">
              <div id="amap-container" style="width: 100%; height: 100%"></div>
            </a-card>
          </div>
        </div>

        <!-- Ежедневный маршрут: сворачиваемый -->
        <a-card title="📅 Ежедневный маршрут" :bordered="false" class="days-card">
          <a-collapse v-model:activeKey="activeDays" accordion>
            <a-collapse-panel
              v-for="(day, index) in tripPlan.days"
              :key="index"
              :id="`day-${index}`"
            >
              <template #header>
                <div class="day-header">
                  <span class="day-title">День {{ day.day_index + 1 }}</span>
                  <span class="day-date">{{ day.date }}</span>
                </div>
              </template>

              <!-- Основная информация о дне -->
              <div class="day-info">
                <div class="info-row">
                  <span class="label">📝 Описание:</span>
                  <span class="value">{{ day.description }}</span>
                </div>
                <div class="info-row">
                  <span class="label">🚗 Транспорт:</span>
                  <span class="value">{{ day.transportation }}</span>
                </div>
                <div class="info-row">
                  <span class="label">🏨 Размещение:</span>
                  <span class="value">{{ day.accommodation }}</span>
                </div>
              </div>

              <!-- Достопримечательности -->
              <a-divider orientation="left">🎯 Достопримечательности</a-divider>
              <a-list
                :data-source="day.attractions"
                :grid="{ gutter: 16, column: 2 }"
              >
                <template #renderItem="{ item, index }">
                  <a-list-item>
                    <a-card :title="item.name" size="small" class="attraction-card">
                      <!-- Кнопки управления в режиме редактирования -->
                      <template #extra v-if="editMode">
                        <a-space>
                          <a-button
                            size="small"
                            @click="moveAttraction(day.day_index, index, 'up')"
                            :disabled="index === 0"
                          >
                            ↑
                          </a-button>
                          <a-button
                            size="small"
                            @click="moveAttraction(day.day_index, index, 'down')"
                            :disabled="index === day.attractions.length - 1"
                          >
                            ↓
                          </a-button>
                          <a-button
                            size="small"
                            danger
                            @click="deleteAttraction(day.day_index, index)"
                          >
                            🗑️
                          </a-button>
                        </a-space>
                      </template>

                      <!-- Фото достопримечательности -->
                      <div class="attraction-image-wrapper">
                        <img
                          :src="getAttractionImage(item.name, index)"
                          :alt="item.name"
                          class="attraction-image"
                          @error="handleImageError"
                        />
                        <div class="attraction-badge">
                          <span class="badge-number">{{ index + 1 }}</span>
                        </div>
                        <div v-if="item.ticket_price" class="price-tag">
                          {{ item.ticket_price }} руб.
                        </div>
                      </div>

                      <!-- Редактируемые поля в режиме редактирования -->
                      <div v-if="editMode">
                        <p><strong>Адрес:</strong></p>
                        <a-input v-model:value="item.address" size="small" style="margin-bottom: 8px" />

                        <p><strong>Время посещения (минуты):</strong></p>
                        <a-input-number v-model:value="item.visit_duration" :min="10" :max="480" size="small" style="width: 100%; margin-bottom: 8px" />

                        <p><strong>Описание:</strong></p>
                        <a-textarea v-model:value="item.description" :rows="2" size="small" style="margin-bottom: 8px" />
                      </div>

                      <!-- Режим просмотра -->
                      <div v-else>
                        <p><strong>Адрес:</strong> {{ item.address }}</p>
                        <p><strong>Время посещения:</strong> {{ item.visit_duration }} мин.</p>
                        <p><strong>Описание:</strong> {{ item.description }}</p>
                        <p v-if="item.rating"><strong>Рейтинг:</strong> {{ item.rating }}⭐</p>
                      </div>
                    </a-card>
                  </a-list-item>
                </template>
              </a-list>

              <!-- Рекомендация отеля -->
              <a-divider v-if="day.hotel" orientation="left">🏨 Рекомендуемое проживание</a-divider>
              <a-card v-if="day.hotel" size="small" class="hotel-card">
                <template #title>
                  <span class="hotel-title">{{ day.hotel.name }}</span>
                </template>
                <a-descriptions :column="2" size="small">
                  <a-descriptions-item label="Адрес">{{ day.hotel.address }}</a-descriptions-item>
                  <a-descriptions-item label="Тип">{{ day.hotel.type }}</a-descriptions-item>
                  <a-descriptions-item label="Ценовой диапазон">{{ day.hotel.price_range }}</a-descriptions-item>
                  <a-descriptions-item label="Рейтинг">{{ day.hotel.rating }}⭐</a-descriptions-item>
                  <a-descriptions-item label="Расстояние" :span="2">{{ day.hotel.distance }}</a-descriptions-item>
                </a-descriptions>
              </a-card>

              <!-- Питание -->
              <a-divider orientation="left">🍽️ Питание</a-divider>
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item
                  v-for="meal in day.meals"
                  :key="meal.type"
                  :label="getMealLabel(meal.type)"
                >
                  {{ meal.name }}
                  <span v-if="meal.description"> — {{ meal.description }}</span>
                </a-descriptions-item>
              </a-descriptions>
            </a-collapse-panel>
          </a-collapse>
        </a-card>

        <a-card id="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0" title="Погода" style="margin-top: 20px" :bordered="false">
        <a-list
          :data-source="tripPlan.weather_info"
          :grid="{ gutter: 16, column: 3 }"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-card size="small" class="weather-card">
                <div class="weather-date">{{ item.date }}</div>
                <div class="weather-info-row">
                  <span class="weather-icon">☀️</span>
                  <div>
                    <div class="weather-label">Днём</div>
                    <div class="weather-value">{{ item.day_weather }} {{ item.day_temp }}°C</div>
                  </div>
                </div>
                <div class="weather-info-row">
                  <span class="weather-icon">🌙</span>
                  <div>
                    <div class="weather-label">Ночью</div>
                    <div class="weather-value">{{ item.night_weather }} {{ item.night_temp }}°C</div>
                  </div>
                </div>
                <div class="weather-wind">
                  💨 {{ item.wind_direction }} {{ item.wind_power }}
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
        </a-card>
      </div>
    </div>

    <a-empty v-else description="Данные плана путешествия не найдены">
      <template #image>
        <div style="font-size: 80px;">🗺️</div>
      </template>
      <template #description>
        <span style="color: #999;">Данные о маршруте отсутствуют, пожалуйста, создайте маршрут</span>
      </template>
      <a-button type="primary" @click="goBack">На главную — создать маршрут</a-button>
    </a-empty>

    <!-- Кнопка «Наверх» -->
    <a-back-top :visibility-height="300">
      <div class="back-top-button">
        ↑
      </div>
    </a-back-top>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan } from '@/types'

const router = useRouter()
const tripPlan = ref<TripPlan | null>(null)
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const attractionPhotos = ref<Record<string, string>>({})
const activeSection = ref('overview')
const activeDays = ref<number[]>([0]) // По умолчанию открываем первый день
let map: any = null

onMounted(async () => {
  const data = sessionStorage.getItem('tripPlan')
  if (data) {
    tripPlan.value = JSON.parse(data)
    // Загружаем фото достопримечательностей
    await loadAttractionPhotos()
    // После рендеринга DOM инициализируем карту
    await nextTick()
    initMap()
  }
})

const goBack = () => {
  router.push('/')
}

// Прокрутка к нужному разделу
const scrollToSection = ({ key }: { key: string }) => {
  activeSection.value = key
  const element = document.getElementById(key)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// Переключение режима редактирования
const toggleEditMode = () => {
  editMode.value = true
  // Сохраняем исходные данные для отмены редактирования
  originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  message.info('Режим редактирования включён')
}

// Сохранение изменений
const saveChanges = () => {
  editMode.value = false
  // Обновляем sessionStorage
  if (tripPlan.value) {
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  }
  message.success('Изменения сохранены')

  // Переинициализируем карту с учётом изменений
  if (map) {
    map.destroy()
  }
  nextTick(() => {
    initMap()
  })
}

// Отмена редактирования
const cancelEdit = () => {
  if (originalPlan.value) {
    tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  }
  editMode.value = false
  message.info('Редактирование отменено')
}

// Удаление достопримечательности
const deleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripPlan.value) return

  const day = tripPlan.value.days[dayIndex]
  if (day.attractions.length <= 1) {
    message.warning('На каждый день должна оставаться хотя бы одна достопримечательность')
    return
  }

  day.attractions.splice(attrIndex, 1)
  message.success('Достопримечательность удалена')
}

// Изменение порядка достопримечательностей
const moveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  if (!tripPlan.value) return

  const day = tripPlan.value.days[dayIndex]
  const attractions = day.attractions

  if (direction === 'up' && attrIndex > 0) {
    [attractions[attrIndex], attractions[attrIndex - 1]] = [attractions[attrIndex - 1], attractions[attrIndex]]
  } else if (direction === 'down' && attrIndex < attractions.length - 1) {
    [attractions[attrIndex], attractions[attrIndex + 1]] = [attractions[attrIndex + 1], attractions[attrIndex]]
  }
}

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = {
    breakfast: 'Завтрак',
    lunch: 'Обед',
    dinner: 'Ужин',
    snack: 'Перекус'
  }
  return labels[type] || type
}

// Загрузка фото всех достопримечательностей
const loadAttractionPhotos = async () => {
  if (!tripPlan.value) return

  const promises: Promise<void>[] = []

  tripPlan.value.days.forEach(day => {
    day.attractions.forEach(attraction => {
      const promise = fetch(`http://localhost:8000/api/poi/photo?name=${encodeURIComponent(attraction.name)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success && data.data.photo_url) {
            attractionPhotos.value[attraction.name] = data.data.photo_url
          }
        })
        .catch(err => {
          console.error(`Ошибка загрузки фото для ${attraction.name}:`, err)
        })

      promises.push(promise)
    })
  })

  await Promise.all(promises)
}

// Получение фото достопримечательности
const getAttractionImage = (name: string, index: number): string => {
  // Если реальное фото уже загружено — возвращаем его
  if (attractionPhotos.value[name]) {
    return attractionPhotos.value[name]
  }

  // Возвращаем цветной SVG-заполнитель (без проблем с CORS)
  const colors = [
    { start: '#667eea', end: '#764ba2' },
    { start: '#f093fb', end: '#f5576c' },
    { start: '#4facfe', end: '#00f2fe' },
    { start: '#43e97b', end: '#38f9d7' },
    { start: '#fa709a', end: '#fee140' }
  ]
  const colorIndex = index % colors.length
  const { start, end } = colors[colorIndex]

  // Используем base64 для избежания проблем с кириллицей
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
    <defs>
      <linearGradient id="grad${index}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${start};stop-opacity:1" />
        <stop offset="100%" style="stop-color:${end};stop-opacity:1" />
      </linearGradient>
    </defs>
    <rect width="400" height="300" fill="url(#grad${index})"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="bold" fill="white">${name}</text>
  </svg>`

  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

// Обработка ошибки загрузки изображения
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  // Используем серый заполнитель
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="18" fill="%23999"%3E%D0%9E%D1%88%D0%B8%D0%B1%D0%BA%D0%B0 %D0%B7%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8%3C/text%3E%3C/svg%3E'
}



// Экспорт в изображение
const exportAsImage = async () => {
  try {
    message.loading({ content: 'Создание изображения...', key: 'export', duration: 0 })

    const element = document.querySelector('.main-content') as HTMLElement
    if (!element) {
      throw new Error('Элемент контента не найден')
    }

    // Создаём отдельный контейнер для экспорта
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#f5f7fa'
    exportContainer.style.padding = '20px'

    // Копируем весь контент
    exportContainer.innerHTML = element.innerHTML

    // Делаем снимок карты
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const mapSnapshot = mapCanvas.toDataURL('image/png')
        const exportMapContainer = exportContainer.querySelector('#amap-container')
        if (exportMapContainer) {
          exportMapContainer.innerHTML = `<img src="${mapSnapshot}" style="width:100%;height:100%;object-fit:cover;" />`
        }
      }
    }

    // Убираем все классы ant-card, заменяем на простые div
    const cards = exportContainer.querySelectorAll('.ant-card')
    cards.forEach((card) => {
      const cardEl = card as HTMLElement
      try {
        cardEl.className = '' // Удаляем все классы
        cardEl.style.setProperty('background-color', '#ffffff')
        cardEl.style.setProperty('border-radius', '12px')
        cardEl.style.setProperty('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.1)')
        cardEl.style.setProperty('margin-bottom', '20px')
        cardEl.style.setProperty('overflow', 'hidden')
      } catch (err) {
        console.error('Ошибка стилизации карточки:', err)
      }
    })

    // Стилизуем заголовки карточек
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      try {
        headEl.style.setProperty('background-color', '#667eea')
        headEl.style.setProperty('color', '#ffffff')
        headEl.style.setProperty('padding', '16px 24px')
        headEl.style.setProperty('font-size', '18px')
        headEl.style.setProperty('font-weight', '600')
      } catch (err) {
        console.error('Ошибка стилизации заголовка карточки:', err)
      }
    })

    // Стилизуем тела карточек
    const cardBodies = exportContainer.querySelectorAll('.ant-card-body')
    cardBodies.forEach((body) => {
      const bodyEl = body as HTMLElement
      bodyEl.style.setProperty('background-color', '#ffffff')
      bodyEl.style.setProperty('padding', '24px')
    })

    // Стилизуем карточки отелей
    const hotelCards = exportContainer.querySelectorAll('.hotel-card')
    hotelCards.forEach((card) => {
      const head = card.querySelector('.ant-card-head') as HTMLElement
      if (head) {
        head.style.setProperty('background-color', '#1976d2')
      }
      (card as HTMLElement).style.setProperty('background-color', '#e3f2fd')
    })

    // Стилизуем карточки погоды
    const weatherCards = exportContainer.querySelectorAll('.weather-card')
    weatherCards.forEach((card) => {
      (card as HTMLElement).style.setProperty('background-color', '#e0f7fa')
    })

    // Стилизуем итог бюджета
    const budgetTotal = exportContainer.querySelector('.budget-total')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#667eea')
      el.style.setProperty('color', '#ffffff')
      el.style.setProperty('padding', '20px')
      el.style.setProperty('border-radius', '12px')
      el.style.setProperty('margin-bottom', '20px')
    }

    // Стилизуем строки бюджета
    const budgetItems = exportContainer.querySelectorAll('.budget-item')
    budgetItems.forEach((item) => {
      const el = item as HTMLElement
      el.style.setProperty('background-color', '#f5f7fa')
      el.style.setProperty('padding', '16px')
      el.style.setProperty('border-radius', '8px')
      el.style.setProperty('margin-bottom', '12px')
    })

    // Добавляем контейнер в body (скрытый)
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)

    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f5f7fa',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    // Удаляем контейнер
    document.body.removeChild(exportContainer)

    // Конвертируем в изображение и скачиваем
    const link = document.createElement('a')
    link.download = `план_путешествия_${tripPlan.value?.city}_${new Date().getTime()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()

    message.success({ content: 'Изображение успешно экспортировано!', key: 'export' })
  } catch (error: any) {
    console.error('Ошибка экспорта изображения:', error)
    message.error({ content: `Ошибка экспорта изображения: ${error.message}`, key: 'export' })
  }
}

// Экспорт в PDF
const exportAsPDF = async () => {
  try {
    message.loading({ content: 'Создание PDF...', key: 'export', duration: 0 })

    const element = document.querySelector('.main-content') as HTMLElement
    if (!element) {
      throw new Error('Элемент контента не найден')
    }

    // Создаём отдельный контейнер для экспорта
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#f5f7fa'
    exportContainer.style.padding = '20px'

    // Копируем весь контент
    exportContainer.innerHTML = element.innerHTML

    // Делаем снимок карты
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const mapSnapshot = mapCanvas.toDataURL('image/png')
        const exportMapContainer = exportContainer.querySelector('#amap-container')
        if (exportMapContainer) {
          exportMapContainer.innerHTML = `<img src="${mapSnapshot}" style="width:100%;height:100%;object-fit:cover;" />`
        }
      }
    }

    // Убираем все классы ant-card, заменяем на простые div
    const cards = exportContainer.querySelectorAll('.ant-card')
    cards.forEach((card) => {
      const cardEl = card as HTMLElement
      try {
        cardEl.className = ''
        cardEl.style.setProperty('background-color', '#ffffff')
        cardEl.style.setProperty('border-radius', '12px')
        cardEl.style.setProperty('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.1)')
        cardEl.style.setProperty('margin-bottom', '20px')
        cardEl.style.setProperty('overflow', 'hidden')
      } catch (err) {
        console.error('Ошибка стилизации карточки:', err)
      }
    })

    // Стилизуем заголовки карточек
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      try {
        headEl.style.setProperty('background-color', '#667eea')
        headEl.style.setProperty('color', '#ffffff')
        headEl.style.setProperty('padding', '16px 24px')
        headEl.style.setProperty('font-size', '18px')
        headEl.style.setProperty('font-weight', '600')
      } catch (err) {
        console.error('Ошибка стилизации заголовка карточки:', err)
      }
    })

    // Стилизуем тела карточек
    const cardBodies = exportContainer.querySelectorAll('.ant-card-body')
    cardBodies.forEach((body) => {
      const bodyEl = body as HTMLElement
      bodyEl.style.setProperty('background-color', '#ffffff')
      bodyEl.style.setProperty('padding', '24px')
    })

    // Стилизуем карточки отелей
    const hotelCards = exportContainer.querySelectorAll('.hotel-card')
    hotelCards.forEach((card) => {
      const head = card.querySelector('.ant-card-head') as HTMLElement
      if (head) {
        head.style.setProperty('background-color', '#1976d2')
      }
      (card as HTMLElement).style.setProperty('background-color', '#e3f2fd')
    })

    // Стилизуем карточки погоды
    const weatherCards = exportContainer.querySelectorAll('.weather-card')
    weatherCards.forEach((card) => {
      (card as HTMLElement).style.setProperty('background-color', '#e0f7fa')
    })

    // Стилизуем итог бюджета
    const budgetTotal = exportContainer.querySelector('.budget-total')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#667eea')
      el.style.setProperty('color', '#ffffff')
      el.style.setProperty('padding', '20px')
      el.style.setProperty('border-radius', '12px')
      el.style.setProperty('margin-bottom', '20px')
    }

    // Стилизуем строки бюджета
    const budgetItems = exportContainer.querySelectorAll('.budget-item')
    budgetItems.forEach((item) => {
      const el = item as HTMLElement
      el.style.setProperty('background-color', '#f5f7fa')
      el.style.setProperty('padding', '16px')
      el.style.setProperty('border-radius', '8px')
      el.style.setProperty('margin-bottom', '12px')
    })

    // Добавляем контейнер в body (скрытый)
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)

    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f5f7fa',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    // Удаляем контейнер
    document.body.removeChild(exportContainer)

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const imgWidth = 210 // Ширина A4 (мм)
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    // Если контент превышает одну страницу — разбиваем на страницы
    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297 // Высота A4

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }

    pdf.save(`план_путешествия_${tripPlan.value?.city}_${new Date().getTime()}.pdf`)

    message.success({ content: 'PDF успешно экспортирован!', key: 'export' })
  } catch (error: any) {
    console.error('Ошибка экспорта PDF:', error)
    message.error({ content: `Ошибка экспорта PDF: ${error.message}`, key: 'export' })
  }
}

// Снимок карты
const captureMapImage = async () => {
  if (!map) return

  try {
    // Получаем контейнер карты
    const mapContainer = document.getElementById('amap-container')
    if (!mapContainer) return

    // Используем функцию снимка карт AMap
    const mapCanvas = mapContainer.querySelector('canvas')
    if (mapCanvas) {
      // Создаём элемент img вместо контейнера карты
      const img = document.createElement('img')
      img.src = mapCanvas.toDataURL('image/png')
      img.style.width = '100%'
      img.style.height = '500px'
      img.style.objectFit = 'cover'
      img.id = 'map-snapshot'

      // Скрываем карту, показываем снимок
      mapContainer.style.display = 'none'
      mapContainer.parentElement?.appendChild(img)
    }
  } catch (error) {
    console.error('Ошибка снимка карты:', error)
  }
}

// Восстановление карты
const restoreMap = () => {
  const mapContainer = document.getElementById('amap-container')
  const snapshot = document.getElementById('map-snapshot')

  if (mapContainer) {
    mapContainer.style.display = 'block'
  }

  if (snapshot) {
    snapshot.remove()
  }
}

// Инициализация карты
const initMap = async () => {
  try {
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,  // JS API Key для веб-клиента карт AMap
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.InfoWindow']
    })

    // Создаём экземпляр карты
    map = new AMap.Map('amap-container', {
      zoom: 12,
      center: [37.617, 55.755], // Центр по умолчанию (Москва)
      viewMode: '3D'
    })

    // Добавляем маркеры достопримечательностей
    addAttractionMarkers(AMap)

    message.success('Карта загружена успешно')
  } catch (error) {
    console.error('Ошибка загрузки карты:', error)
    message.error('Ошибка загрузки карты')
  }
}

// Добавление маркеров достопримечательностей
const addAttractionMarkers = (AMap: any) => {
  if (!tripPlan.value) return

  const markers: any[] = []
  const allAttractions: any[] = []

  // Собираем все достопримечательности
  tripPlan.value.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      if (attraction.location && attraction.location.longitude && attraction.location.latitude) {
        allAttractions.push({
          ...attraction,
          dayIndex,
          attrIndex
        })
      }
    })
  })

  // Создаём маркеры
  allAttractions.forEach((attraction, index) => {
    const marker = new AMap.Marker({
      position: [attraction.location.longitude, attraction.location.latitude],
      title: attraction.name,
      label: {
        content: `<div style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${index + 1}</div>`,
        offset: new AMap.Pixel(0, -30)
      }
    })

    // Создаём информационное окно
    const infoWindow = new AMap.InfoWindow({
      content: `
        <div style="padding: 10px;">
          <h4 style="margin: 0 0 8px 0;">${attraction.name}</h4>
          <p style="margin: 4px 0;"><strong>Адрес:</strong> ${attraction.address}</p>
          <p style="margin: 4px 0;"><strong>Время посещения:</strong> ${attraction.visit_duration} мин.</p>
          <p style="margin: 4px 0;"><strong>Описание:</strong> ${attraction.description}</p>
          <p style="margin: 4px 0; color: #1890ff;"><strong>День ${attraction.dayIndex + 1}, достопримечательность ${attraction.attrIndex + 1}</strong></p>
        </div>
      `,
      offset: new AMap.Pixel(0, -30)
    })

    // При клике на маркер показываем информационное окно
    marker.on('click', () => {
      infoWindow.open(map, marker.getPosition())
    })

    markers.push(marker)
  })

  // Добавляем маркеры на карту
  map.add(markers)

  // Автоматически подбираем масштаб для всех маркеров
  if (allAttractions.length > 0) {
    map.setFitView(markers)
  }

  // Рисуем маршруты
  drawRoutes(AMap, allAttractions)
}

// Рисование маршрутов
const drawRoutes = (AMap: any, attractions: any[]) => {
  if (attractions.length < 2) return

  // Группируем по дням
  const dayGroups: any = {}
  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) {
      dayGroups[attr.dayIndex] = []
    }
    dayGroups[attr.dayIndex].push(attr)
  })

  // Рисуем маршрут для каждого дня
  Object.values(dayGroups).forEach((dayAttractions: any) => {
    if (dayAttractions.length < 2) return

    const path = dayAttractions.map((attr: any) => [
      attr.location.longitude,
      attr.location.latitude
    ])

    const polyline = new AMap.Polyline({
      path: path,
      strokeColor: '#1890ff',
      strokeWeight: 4,
      strokeOpacity: 0.8,
      strokeStyle: 'solid',
      showDir: true // Показывать стрелки направления
    })

    map.add(polyline)
  })
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 20px;
}

.page-header {
  max-width: 1200px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: fadeInDown 0.6s ease-out;
}

.back-button {
  border-radius: 8px;
  font-weight: 500;
}

/* Макет контента */
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
}

.side-nav {
  width: 240px;
  flex-shrink: 0;
}

.side-nav :deep(.ant-menu) {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background: white;
}

.side-nav :deep(.ant-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.side-nav :deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.side-nav :deep(.ant-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
}

.main-content {
  flex: 1;
  min-width: 0;
}

/* Стили изображений достопримечательностей */
.attraction-image-wrapper {
  position: relative;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.attraction-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.attraction-image-wrapper:hover .attraction-image {
  transform: scale(1.05);
}

.attraction-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.badge-number {
  font-size: 18px;
}

.price-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 77, 79, 0.9);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Стили карточек погоды */
.weather-card {
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  border: none !important;
  transition: all 0.3s ease;
}

.weather-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.weather-date {
  font-size: 16px;
  font-weight: bold;
  color: #00796b;
  margin-bottom: 12px;
  text-align: center;
}

.weather-info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.weather-icon {
  font-size: 24px;
}

.weather-label {
  font-size: 12px;
  color: #666;
}

.weather-value {
  font-size: 16px;
  font-weight: 600;
  color: #00796b;
}

.weather-wind {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 121, 107, 0.2);
  text-align: center;
  color: #00796b;
  font-size: 14px;
}

/* Кнопка «Наверх» */
.back-top-button {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-top-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

/* Стили карточек отелей */
.hotel-card {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: none !important;
}

.hotel-card :deep(.ant-card-head) {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
}

.hotel-title {
  color: white !important;
  font-weight: 600;
}

/* Верхний блок */
.top-info-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.left-info {
  flex: 0 0 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-map {
  flex: 1;
}

/* Карточка обзора маршрута */
.overview-card {
  height: fit-content;
}

.overview-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.info-value {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
}

/* Карточка бюджета */
.budget-card {
  height: fit-content;
}

.budget-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.budget-item {
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.budget-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.budget-value {
  font-size: 20px;
  font-weight: 700;
  color: #1890ff;
}

.budget-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.total-label {
  font-size: 16px;
  font-weight: 600;
}

.total-value {
  font-size: 28px;
  font-weight: 700;
}

/* Карточка карты */
.map-card {
  height: 100%;
  min-height: 500px;
}

.map-card :deep(.ant-card-body) {
  height: calc(100% - 57px);
  padding: 0;
}

/* Карточка ежедневного маршрута */
.days-card {
  margin-top: 20px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.day-date {
  font-size: 14px;
  color: #999;
}

.day-info {
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.info-row .value {
  color: #333;
  flex: 1;
}

/* Оптимизация стилей карточек */
:deep(.ant-card) {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out;
}

:deep(.ant-card:hover) {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

:deep(.ant-card-head) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  border-radius: 12px 12px 0 0;
  font-weight: 600;
}

:deep(.ant-card-head-title) {
  color: white !important;
  font-size: 18px;
}

:deep(.ant-card-head-title span) {
  color: white !important;
}

/* Стили аккордеона */
:deep(.ant-collapse) {
  border: none;
  background: transparent;
}

:deep(.ant-collapse-item) {
  margin-bottom: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.ant-collapse-header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  padding: 16px 20px !important;
  font-weight: 600;
}

:deep(.ant-collapse-content) {
  border-top: 1px solid #e8e8e8;
}

:deep(.ant-collapse-content-box) {
  padding: 20px;
}

/* Стили статистики */
:deep(.ant-statistic-title) {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

:deep(.ant-statistic-content) {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
}

/* Стили списка достопримечательностей */
:deep(.ant-list-item) {
  transition: all 0.3s ease;
}

:deep(.ant-list-item:hover) {
  transform: scale(1.02);
}

/* Анимации */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Адаптивный дизайн */
@media (max-width: 768px) {
  .result-container {
    padding: 20px 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
