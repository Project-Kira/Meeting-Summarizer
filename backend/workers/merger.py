from typing import List, Dict, Any
from difflib import SequenceMatcher


class SummaryMerger:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    def merge_summaries(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged = {
            "summary": "",
            "agenda": [],
            "decisions": [],
            "action_items": [],
            "topics": [],
        }
        
        all_summaries = []
        all_decisions = []
        all_action_items = []
        all_topics = []
        all_agenda = []
        
        for summary in summaries:
            if isinstance(summary, dict):
                content = summary
            else:
                content = summary
            
            if "summary" in content:
                all_summaries.append(content["summary"])
            if "decisions" in content:
                all_decisions.extend(content["decisions"])
            if "action_items" in content:
                all_action_items.extend(content["action_items"])
            if "topics" in content:
                all_topics.extend(content["topics"])
            if "agenda" in content:
                all_agenda.extend(content["agenda"])
        
        merged["summary"] = " ".join(all_summaries)
        merged["agenda"] = self._deduplicate_list(all_agenda)
        merged["decisions"] = self._deduplicate_decisions(all_decisions)
        merged["action_items"] = self._deduplicate_action_items(all_action_items)
        merged["topics"] = self._deduplicate_topics(all_topics)
        
        return merged

    def _deduplicate_list(self, items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items:
            if item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)
        return result

    def _deduplicate_decisions(self, decisions: List[Dict]) -> List[Dict]:
        unique = []
        seen_texts = []
        
        for decision in decisions:
            text = decision.get("text", "")
            is_duplicate = False
            
            for seen_text in seen_texts:
                if self._similarity(text, seen_text) > self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(decision)
                seen_texts.append(text)
        
        return sorted(unique, key=lambda x: x.get("confidence", 0), reverse=True)

    def _deduplicate_action_items(self, action_items: List[Dict]) -> List[Dict]:
        unique = []
        seen_texts = []
        
        for item in action_items:
            text = item.get("text", "")
            is_duplicate = False
            duplicate_idx = -1
            
            for idx, seen_text in enumerate(seen_texts):
                if self._similarity(text, seen_text) > self.similarity_threshold:
                    is_duplicate = True
                    duplicate_idx = idx
                    break
            
            if is_duplicate:
                existing = unique[duplicate_idx]
                if not existing.get("owner") and item.get("owner"):
                    existing["owner"] = item["owner"]
                if not existing.get("due_date_iso") and item.get("due_date_iso"):
                    existing["due_date_iso"] = item["due_date_iso"]
                if item.get("confidence", 0) > existing.get("confidence", 0):
                    existing["confidence"] = item["confidence"]
            else:
                unique.append(item)
                seen_texts.append(text)
        
        return sorted(unique, key=lambda x: x.get("confidence", 0), reverse=True)

    def _deduplicate_topics(self, topics: List[Dict]) -> List[Dict]:
        unique = []
        seen_names = []
        
        for topic in topics:
            name = topic.get("name", "")
            is_duplicate = False
            
            for seen_name in seen_names:
                if self._similarity(name, seen_name) > self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(topic)
                seen_names.append(name)
        
        return sorted(unique, key=lambda x: x.get("confidence", 0), reverse=True)

    def _similarity(self, text1: str, text2: str) -> float:
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
