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
        """Форматирует красивый, легко читаемый аналитический отчет в стиле лонгрида"""
        report_lines = []

        total_msgs = content_analysis.get('total_messages', 0)

        # Краткий вывод — живой нарративный текст
        report_lines.append("## 📖 Что происходило сегодня\n\n")

        if total_msgs == 0:
            report_lines.append(
                "Сегодня в отслеживаемых каналах было тихо — новых постов не появилось.\n\n"
                "Но это не значит, что рынок стоит на месте. Ниже — обзор того, что происходит "
                "в кальянной индустрии на основе накопленных данных за последний период."
            )
        else:
            # Собираем живой рассказ о дне
            story_parts = []
            
            # Начало истории
            story_parts.append(f"За сегодня в кальянном инфополе появилось **{total_msgs} новых постов** из {len(content_analysis.get('channels_activity', {}))} каналов.")
            
            # Активность каналов
            if insights:
                activity = next((i for i in insights if i["type"] == "activity"), None)
                if activity:
                    channel_name = activity['value'].split('(')[0].strip()
                    story_parts.append(f"Самым активным оказался канал **{channel_name}**.")
            
            # Вовлечённость
            if insights:
                engagement = next((i for i in insights if i["type"] == "engagement"), None)
                if engagement:
                    channel_name = engagement['value'].split('(')[0].strip()
                    story_parts.append(f"А больше всего внимания аудитории собрал контент от **{channel_name}**.")
            
            # Бренды
            competitor_brands = []
            if trends_data and trends_data.get("top_brands"):
                focus_brands = {"adalya", "tangiers"}
                for brand, count in trends_data["top_brands"]:
                    if brand.lower() not in focus_brands:
                        competitor_brands.append((brand, count))
            
            if competitor_brands:
                top_3 = competitor_brands[:3]
                brands_text = ", ".join([f"**{b.title()}**" for b, c in top_3])
                story_parts.append(f"В лентах чаще всего мелькали бренды: {brands_text}.")
            
            # Тональность
            if insights:
                sentiment_insight = next((i for i in insights if i["type"] == "sentiment"), None)
                if sentiment_insight:
                    sentiment_text = sentiment_insight['value'].lower()
                    story_parts.append(f"Общий настрой обсуждений — **{sentiment_text}**.")
            
            # Если ничего не собрали
            if not story_parts:
                story_parts.append("Активность распределена равномерно — никаких ярких всплесков не наблюдалось.")
            
            # Объединяем в читаемый текст
            report_lines.append(" ".join(story_parts) + "\n")

        # Ключевые метрики — более читаемо
        if total_msgs > 0:
            report_lines.append("\n\n---\n\n")
            report_lines.append("## 📊 В цифрах\n\n")
            
            total_views = content_analysis.get('total_views', 0)
            avg_views = content_analysis.get('avg_views_per_message', 0)
            media_ratio = content_analysis.get('media_ratio', 0) * 100
            
            report_lines.append(
                f"Всего собрано **{total_msgs} постов**, которые набрали **{total_views:,} просмотров**. "
                f"В среднем каждый пост получил **{avg_views:.0f} просмотров**.\n\n"
            )
            
            if media_ratio > 0:
                report_lines.append(
                    f"**{media_ratio:.0f}%** контента — это фото и видео, остальное — текстовые посты.\n"
                )

        # Активность по каналам — более читаемо
        if content_analysis.get('channels_activity') and total_msgs > 0:
            report_lines.append("\n\n---\n\n")
            report_lines.append("## 📱 Кто и как писал\n\n")
            
            sorted_channels = sorted(
                content_analysis['channels_activity'].items(),
                key=lambda x: x[1]['messages'],
                reverse=True,
            )
            
            for idx, (channel, stats) in enumerate(sorted_channels, 1):
                if stats['messages'] > 0:
                    # Более живое описание
                    media_info = f", из них {stats['media_count']} с фото/видео" if stats['media_count'] > 0 else ""
                    line = (
                        f"**{idx}. {channel}** опубликовал {stats['messages']} постов{media_info}. "
                        f"Средняя вовлечённость — {stats['avg_views']:.0f} просмотров на пост.\n\n"
                    )
                    report_lines.append(line)

        # Популярные темы — более читаемо
        if content_analysis.get('topics') and total_msgs > 0:
            report_lines.append("\n---\n\n")
            report_lines.append("## 💬 О чём говорили\n\n")
            
            top_topics = content_analysis['topics'].most_common(5)
            topics_list = []
            for topic, count in top_topics:
                topics_list.append(f"**{topic}** ({count} раз)")
            
            if topics_list:
                report_lines.append("Основные темы дня: " + ", ".join(topics_list) + ".\n")

        # Новинки, продукты, вкусы (по трендам) — общий рынок, без фокуса на Adalya/Tangiers
        if trends_data:
            brands = trends_data.get("top_brands") or []
            products = trends_data.get("top_products") or []
            flavors = trends_data.get("top_flavors") or []
            events = trends_data.get("events") or []
            business_updates = trends_data.get("business_updates") or []

            if products or flavors or events or business_updates:
                report_lines.append("\n---\n\n")
                report_lines.append("## 🎯 Что в тренде\n\n")

                # Бренды — более читаемо
                focus_brands = {"adalya", "tangiers"}
                competitor_brands = [
                    (b, c) for b, c in brands if b.lower() not in focus_brands
                ]
                if competitor_brands:
                    top_brands_list = [f"**{b.title()}** ({c})" for b, c in competitor_brands[:5]]
                    report_lines.append(
                        f"**Бренды дня:** {', '.join(top_brands_list)}.\n\n"
                    )

                if products:
                    products_list = [f"**{p.title()}** ({c})" for p, c in products[:5]]
                    report_lines.append(
                        f"**Продукты:** {', '.join(products_list)}.\n\n"
                    )

                if flavors:
                    flavors_list = [f"**{f.title()}** ({c})" for f, c in flavors[:5]]
                    report_lines.append(
                        f"**Вкусы:** {', '.join(flavors_list)}.\n\n"
                    )

                if events:
                    report_lines.append("**События и мероприятия:**\n\n")
                    for ev in events[:3]:
                        ev_text = ev['text'][:120].strip()
                        if len(ev['text']) > 120:
                            ev_text += "..."
                        report_lines.append(f"• [{ev['channel']}] {ev_text}\n")
                    report_lines.append("")

                if business_updates:
                    report_lines.append("**Бизнес-новости:**\n\n")
                    for bu in business_updates[:3]:
                        bu_text = bu['text'][:120].strip()
                        if len(bu['text']) > 120:
                            bu_text += "..."
                        report_lines.append(f"• [{bu['channel']}] {bu_text}\n")
                    report_lines.append("")

        # Тональность — более читаемо
        if sentiment_analysis and total_msgs > 0:
            report_lines.append("\n---\n\n")
            report_lines.append("## 😊 Настроение аудитории\n\n")
            
            total = sum(sentiment_analysis.values())
            sentiment_parts = []
            
            for sentiment, count in sentiment_analysis.items():
                if count > 0:
                    pct = (count / total * 100) if total > 0 else 0
                    label = {
                        "positive": "позитивных",
                        "negative": "негативных",
                        "neutral": "нейтральных",
                    }.get(sentiment, sentiment)
                    sentiment_parts.append(f"**{pct:.0f}%** {label}")
            
            if sentiment_parts:
                report_lines.append("Тон обсуждений: " + ", ".join(sentiment_parts) + ".\n")

        # Отдельный блок по брендам фокуса (Adalya / Tangiers)
        if brand_mentions:
            report_lines.append("\n---\n\n")
            report_lines.append("## 🎯 Фокус: Adalya и Tangiers\n\n")
            report_lines.append(brand_mentions.strip())

        return "\n".join(report_lines)
