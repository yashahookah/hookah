"""
Продвинутый аналитический движок для анализа контента Telegram каналов
"""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
import os

class AnalyticsEngine:
    def __init__(self):
        self.analytics_file = 'analytics_data.json'
        self.load_analytics()
    
    def load_analytics(self):
        """Загружает аналитические данные"""
        if os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                self.analytics = json.load(f)
        else:
            self.analytics = {
                'content_analysis': {},
                'engagement_metrics': {},
                'topic_clusters': {},
                'sentiment_analysis': {},
                'influencer_activity': {},
                'market_insights': {}
            }
    
    def save_analytics(self):
        """Сохраняет аналитические данные"""
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(self.analytics, f, ensure_ascii=False, indent=2)
    
    def analyze_content(self, messages_by_channel):
        """Глубокий анализ контента"""
        analysis = {
            'total_messages': 0,
            'total_views': 0,
            'avg_views_per_message': 0,
            'channels_activity': {},
            'content_types': Counter(),
            'topics': Counter(),
            'engagement_by_channel': {},
            'peak_hours': Counter(),
            'media_ratio': 0,
            'text_length_stats': {'min': 0, 'max': 0, 'avg': 0}
        }
        
        all_texts = []
        total_media = 0
        
        for channel_name, messages in messages_by_channel.items():
            channel_stats = {
                'messages': len(messages),
                'views': 0,
                'avg_views': 0,
                'media_count': 0,
                'text_lengths': []
            }
            
            for msg in messages:
                analysis['total_messages'] += 1

                # Безопасно приводим просмотры к числу (некоторые сообщения могут иметь None)
                raw_views = msg.get('views')
                views = raw_views if isinstance(raw_views, (int, float)) and raw_views >= 0 else 0

                analysis['total_views'] += views
                channel_stats['views'] += views
                
                if msg.get('has_media'):
                    total_media += 1
                    channel_stats['media_count'] += 1
                    analysis['content_types']['media'] += 1
                
                text = msg.get('text', '')
                if text:
                    all_texts.append(text)
                    text_len = len(text)
                    channel_stats['text_lengths'].append(text_len)
                    analysis['content_types']['text'] += 1
                    
                    # Определение тематики
                    topics = self.identify_topics(text)
                    for topic in topics:
                        analysis['topics'][topic] += 1
                
                # Анализ времени публикации
                hour = msg.get('date', datetime.now()).hour if isinstance(msg.get('date'), datetime) else datetime.now().hour
                analysis['peak_hours'][hour] += 1
            
            # Статистика по каналу
            if channel_stats['messages'] > 0:
                channel_stats['avg_views'] = channel_stats['views'] / channel_stats['messages']
                if channel_stats['text_lengths']:
                    channel_stats['avg_text_length'] = sum(channel_stats['text_lengths']) / len(channel_stats['text_lengths'])
                else:
                    channel_stats['avg_text_length'] = 0
            
            analysis['channels_activity'][channel_name] = channel_stats
            analysis['engagement_by_channel'][channel_name] = {
                'total_views': channel_stats['views'],
                'avg_views': channel_stats['avg_views'],
                'engagement_rate': channel_stats['avg_views'] if channel_stats['messages'] > 0 else 0
            }
        
        # Общая статистика
        if analysis['total_messages'] > 0:
            analysis['avg_views_per_message'] = analysis['total_views'] / analysis['total_messages']
            analysis['media_ratio'] = total_media / analysis['total_messages']
        
        if all_texts:
            lengths = [len(t) for t in all_texts]
            analysis['text_length_stats'] = {
                'min': min(lengths),
                'max': max(lengths),
                'avg': sum(lengths) / len(lengths)
            }
        
        return analysis
    
    def identify_topics(self, text):
        """Определяет темы в тексте"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            'новинки': ['новинка', 'новый', 'запуск', 'релиз', 'new', 'launch', 'release'],
            'цены': ['цена', 'стоимость', 'скидка', 'акция', 'распродажа', 'price', 'sale', 'discount'],
            'обзоры': ['обзор', 'review', 'тест', 'проверка', 'test'],
            'события': ['выставка', 'фестиваль', 'мероприятие', 'event', 'festival', 'exhibition'],
            'советы': ['совет', 'как', 'рекомендация', 'tip', 'advice', 'how to'],
            'вопросы': ['вопрос', 'помогите', 'подскажите', 'question', 'help'],
            'продажи': ['купить', 'продажа', 'магазин', 'buy', 'sale', 'shop'],
            'техника': ['кальян', 'чаша', 'уголь', 'hookah', 'bowl', 'coals'],
            'вкусы': ['вкус', 'табак', 'flavor', 'tobacco', 'taste'],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def analyze_sentiment(self, messages_by_channel):
        """Анализ тональности (базовый)"""
        sentiment_keywords = {
            'positive': ['отлично', 'супер', 'класс', 'нравится', 'рекомендую', 'лучший', 
                        'great', 'awesome', 'love', 'best', 'excellent', '👍', '❤️'],
            'negative': ['плохо', 'ужасно', 'не нравится', 'разочарован', 'проблема',
                        'bad', 'terrible', 'disappointed', 'problem', 'issue', '👎'],
            'neutral': []
        }
        
        sentiment_counts = Counter()
        
        for channel_name, messages in messages_by_channel.items():
            for msg in messages:
                text = msg.get('text', '').lower()
                if not text:
                    continue
                
                # Простой анализ тональности
                positive_score = sum(1 for word in sentiment_keywords['positive'] if word in text)
                negative_score = sum(1 for word in sentiment_keywords['negative'] if word in text)
                
                if positive_score > negative_score:
                    sentiment_counts['positive'] += 1
                elif negative_score > positive_score:
                    sentiment_counts['negative'] += 1
                else:
                    sentiment_counts['neutral'] += 1
        
        return dict(sentiment_counts)
    
    def generate_insights(self, content_analysis, sentiment_analysis, trends_data):
        """Генерирует инсайты на основе анализа"""
        insights = []
        
        # Если за период не было сообщений, не строим операционные инсайты
        if not content_analysis or content_analysis.get('total_messages', 0) == 0:
            return insights
        
        # Инсайт 1: Активность каналов
        if content_analysis.get('channels_activity'):
            most_active = max(
                content_analysis['channels_activity'].items(),
                key=lambda x: x[1]['messages']
            )
            insights.append({
                'type': 'activity',
                'title': 'Самый активный канал',
                'value': f"{most_active[0]} ({most_active[1]['messages']} сообщений)",
                'insight': f"Канал {most_active[0]} показывает наибольшую активность сегодня"
            })
        
        # Инсайт 2: Вовлеченность
        if content_analysis.get('engagement_by_channel'):
            most_engaged = max(
                content_analysis['engagement_by_channel'].items(),
                key=lambda x: x[1]['avg_views']
            )
            insights.append({
                'type': 'engagement',
                'title': 'Высокая вовлеченность',
                'value': f"{most_engaged[0]} (среднее {most_engaged[1]['avg_views']:.0f} просмотров)",
                'insight': f"Контент {most_engaged[0]} получает наибольшее внимание аудитории"
            })
        
        # Инсайт 3: Популярные темы
        if content_analysis.get('topics'):
            top_topics = content_analysis['topics'].most_common(3)
            topics_str = ', '.join([f"{topic} ({count})" for topic, count in top_topics])
            insights.append({
                'type': 'topics',
                'title': 'Популярные темы',
                'value': topics_str,
                'insight': f"Наиболее обсуждаемые темы: {topics_str}"
            })
        
        # Инсайт 4: Тон обсуждений
        if sentiment_analysis:
            total = sum(sentiment_analysis.values())
            if total > 0:
                positive_pct = (sentiment_analysis.get('positive', 0) / total) * 100
                insights.append({
                    'type': 'sentiment',
                    'title': 'Тон обсуждений',
                    'value': f"{positive_pct:.1f}% позитивных упоминаний",
                    'insight': f"Большинство обсуждений имеют {'позитивный' if positive_pct > 50 else 'нейтральный/негативный'} тон"
                })
        
        # Инсайт 5: Пиковые часы
        if content_analysis.get('peak_hours'):
            peak_hour = content_analysis['peak_hours'].most_common(1)[0]
            insights.append({
                'type': 'timing',
                'title': 'Пик активности',
                'value': f"{peak_hour[0]}:00 ({peak_hour[1]} сообщений)",
                'insight': f"Наибольшая активность наблюдается в {peak_hour[0]}:00"
            })
        
        return insights
    
    def format_analytics_report(self, content_analysis, sentiment_analysis, insights, brand_mentions, trends_data=None):
        """Форматирует красивый, легко читаемый аналитический отчет (markdown)"""
        report_lines = []

        # Краткий вывод (самое важное сверху, в виде нормального текста)
        report_lines.append("## 🧾 Краткий вывод\n")

        total_msgs = content_analysis.get('total_messages', 0)

        # Отдельный сценарий: за период не было новых постов
        if total_msgs == 0:
            report_lines.append(
                "За выбранный период в отслеживаемых каналах не было новых постов.\n\n"
                "Ниже — обзор рынка, брендов и цен, основанный на накопленных данных за более длинный период."
            )
        else:
            # Попробуем собрать небольшой «обзор дня» в пару предложений
            summary_sentences = []

            # 1) Используем инсайты (активность, вовлечённость, тональность)
            if insights:
                # Берём только самые базовые инсайты
                activity = next((i for i in insights if i["type"] == "activity"), None)
                engagement = next((i for i in insights if i["type"] == "engagement"), None)
                sentiment_insight = next((i for i in insights if i["type"] == "sentiment"), None)

                if activity:
                    summary_sentences.append(
                        f"По активности за период выделяется канал {activity['value']}."
                    )
                if engagement:
                    summary_sentences.append(
                        f"Больше всего внимания аудитории собирает контент канала {engagement['value']}."
                    )
                if sentiment_insight:
                    summary_sentences.append(
                        f"В целом тон обсуждений — {sentiment_insight['value'].lower()}."
                    )

            # 2) Подсветим конкурентов по брендам (без Adalya и Tangiers)
            competitor_brands = []
            if trends_data and trends_data.get("top_brands"):
                focus_brands = {"adalya", "tangiers"}
                for brand, count in trends_data["top_brands"]:
                    if brand.lower() not in focus_brands:
                        competitor_brands.append((brand, count))

            if competitor_brands:
                top_competitors = ", ".join(
                    [f"{b.title()} ({c})" for b, c in competitor_brands[:3]]
                )
                summary_sentences.append(
                    f"Среди брендов в ленте чаще всего всплывали конкуренты: {top_competitors}."
                )

            # Если ничего осмысленного не собрали — fallback
            if not summary_sentences:
                report_lines.append(
                    "За период нет ярко выраженных всплесков активности — обсуждения распределены достаточно ровно."
                )
            else:
                # Разбиваем на абзацы для читаемости
                report_lines.append("\n\n".join(summary_sentences))

        # Ключевые метрики
        report_lines.append("\n\n---\n\n")
        report_lines.append("## 📈 Ключевые метрики\n\n")
        report_lines.append(f"- **Сообщений**: {content_analysis.get('total_messages', 0)}\n")
        report_lines.append(f"- **Просмотров всего**: {content_analysis.get('total_views', 0):,}\n")
        report_lines.append(
            f"- **Среднее просмотров на пост**: {content_analysis.get('avg_views_per_message', 0):.1f}\n"
        )
        report_lines.append(
            f"- **Доля медиа‑контента**: {content_analysis.get('media_ratio', 0) * 100:.1f}%"
        )

        # Активность по каналам
        if content_analysis.get('channels_activity'):
            report_lines.append("\n\n---\n\n")
            report_lines.append("## 📡 Активность по каналам\n\n")
            sorted_channels = sorted(
                content_analysis['channels_activity'].items(),
                key=lambda x: x[1]['messages'],
                reverse=True,
            )
            for channel, stats in sorted_channels:
                line = (
                    f"- **{channel}**: "
                    f"{stats['messages']} постов, "
                    f"среднее {stats['avg_views']:.0f} просмотров, "
                    f"медиа: {stats['media_count']} шт.\n"
                )
                report_lines.append(line)
            report_lines.append("")  # Пустая строка в конце списка

        # Популярные темы (о чем в целом говорят)
        if content_analysis.get('topics'):
            report_lines.append("\n---\n\n")
            report_lines.append("## 🏷️ О чём говорят\n\n")
            top_topics = content_analysis['topics'].most_common(5)
            for topic, count in top_topics:
                report_lines.append(f"- **{topic}**: {count} упоминаний\n")
            report_lines.append("")  # Пустая строка в конце списка

        # Новинки, продукты, вкусы (по трендам) — общий рынок, без фокуса на Adalya/Tangiers
        if trends_data:
            brands = trends_data.get("top_brands") or []
            products = trends_data.get("top_products") or []
            flavors = trends_data.get("top_flavors") or []
            events = trends_data.get("events") or []
            business_updates = trends_data.get("business_updates") or []

            if products or flavors or events or business_updates:
                report_lines.append("\n---\n")
                report_lines.append("## 🆕 Новинки, продукты и движ рынка\n")

                # Бренды‑лидеры дня (конкурентная картина, без Adalya/Tangiers)
                focus_brands = {"adalya", "tangiers"}
                competitor_brands = [
                    (b, c) for b, c in brands if b.lower() not in focus_brands
                ]
                if competitor_brands:
                    report_lines.append("**Бренды, о которых говорили чаще всего (кроме Adalya/Tangiers):**\n")
                    for brand, count in competitor_brands[:5]:
                        report_lines.append(f"- {brand.title()} — {count} упоминаний\n")
                    report_lines.append("")

                if products:
                    report_lines.append("**Продукты/категории, которые чаще всего всплывали:**\n")
                    for product, count in products[:5]:
                        report_lines.append(f"- {product.title()} — {count} упоминаний\n")
                    report_lines.append("")

                if flavors:
                    report_lines.append("**Вкусы и сочетания, о которых писали чаще всего:**\n")
                    for flavor, count in flavors[:5]:
                        report_lines.append(f"- {flavor.title()} — {count} упоминаний\n")
                    report_lines.append("")

                if events:
                    report_lines.append("**События и активность:**\n")
                    for ev in events:
                        report_lines.append(f"- [{ev['channel']}] {ev['text']}\n")
                    report_lines.append("")

                if business_updates:
                    report_lines.append("**Бизнес‑обновления (акции, новинки, запуски):**\n")
                    for bu in business_updates:
                        report_lines.append(f"- [{bu['channel']}] {bu['text']}\n")
                    report_lines.append("")

        # Тональность
        if sentiment_analysis:
            report_lines.append("\n---\n")
            report_lines.append("## 😊 Тональность обсуждений\n")
            total = sum(sentiment_analysis.values())
            for sentiment, count in sentiment_analysis.items():
                pct = (count / total * 100) if total > 0 else 0
                label = {
                    "positive": "Позитив",
                    "negative": "Негатив",
                    "neutral": "Нейтрально",
                }.get(sentiment, sentiment)
                report_lines.append(f"- **{label}**: {count} ({pct:.1f}%)")

        # Отдельный блок по брендам фокуса (Adalya / Tangiers)
        if brand_mentions:
            report_lines.append("\n---\n")
            report_lines.append("## 🎯 Фокус: Adalya и Tangiers\n")
            report_lines.append(brand_mentions.strip())

        return "\n".join(report_lines)
