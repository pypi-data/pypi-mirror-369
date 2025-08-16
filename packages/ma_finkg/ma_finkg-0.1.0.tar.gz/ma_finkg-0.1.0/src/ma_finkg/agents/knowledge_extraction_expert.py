"""
Knowledge Extraction Expert - Orchestrates NER and RE sub-agents.

This agent manages the core information extraction tasks using specialized
sub-agents for Named Entity Recognition and Relation Extraction.
"""

import json
from typing import Dict, Any, List, Tuple, Set
from langchain_core.messages import HumanMessage, SystemMessage
import json_repair

from models import GraphState, Entity, Triple, FinancialOntology
from utils import load_prompts, print_progress, get_elapsed_time, spinner
from utils.llm_factory import create_openrouter_llm


class NERExpert:
    """
    Named Entity Recognition sub-agent that extracts entities based on ontology.
    """
    
    def __init__(self, model_name: str = "openai/gpt-3.5-turbo"):
        self.llm = create_openrouter_llm(model_name)
    
    def extract_entities_by_type(self, text: str, entity_type: str, 
                                ontology: FinancialOntology) -> List[Entity]:
        """
        Extracts all entities of a specific type from text.
        """
        entity_info = ontology.entity_types[entity_type]
        prompts = load_prompts()['knowledge_extraction_expert']
        prompt = prompts['ner_entity_extraction_prompt'].format(
            entity_type=entity_type,
            text=text
        )

        try:
            with spinner(f"Extracting {entity_type}"):
                response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content.strip()
            
            # Parse JSON with repair if needed
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                data = json.loads(json_repair.repair_json(response_text))
            
            # Extract entities from response
            entities = []
            if entity_type in data:
                for entity_text in data[entity_type]:
                    if entity_text and entity_text.strip():
                        entities.append(Entity(
                            text=entity_text.strip(),
                            entity_type=entity_type
                        ))
            
            return entities
            
        except Exception as e:
            print(f"Error in NER extraction for {entity_type}: {e}")
            return []



class REExpert:
    """
    Relation Extraction sub-agent that extracts relations between entities.
    """
    
    def __init__(self, model_name: str = "openai/gpt-3.5-turbo"):
        self.llm = create_openrouter_llm(model_name)
    
    def extract_relations_by_type(self, text: str, relation_type: str, 
                                 entities: List[Entity], ontology: FinancialOntology) -> Tuple[List[Triple], Set[str]]:
        """
        Extracts relations of a specific type using two-step approach.
        """
        if relation_type not in ontology.relation_types:
            return [], set()
        
        
        rel_sig = ontology.relation_types[relation_type]
        head_types = set(rel_sig.head_types)
        tail_types = set(rel_sig.tail_types)
        
        head_entities = [e for e in entities if e.entity_type in head_types]
        tail_entities = [e for e in entities if e.entity_type in tail_types]
        
        triples = []
        missing_entities = set()
        
        # Step 1: Find potential head entities for this relation
        head_candidates = self._extract_head_entities(text, relation_type, list(head_types))
        elapsed = get_elapsed_time()
        print_progress(f"[{elapsed:.1f}s] Found {len(head_candidates)} head candidates for {relation_type}")
        
        # Step 2: For each head entity, find corresponding tail entities
        for i, head_entity in enumerate(head_candidates, 1):
            elapsed = get_elapsed_time()
            print_progress(f"[{elapsed:.1f}s] Processing head {i}/{len(head_candidates)}: {head_entity}")
            
            # Emergency timeout protection
            if elapsed > 3600:  # 1 hour timeout
                print(f"\nEMERGENCY TIMEOUT: Stopping relation extraction after 1 hour")
                break
                
            # Check if head entity exists in NER results (exact match)
            matching_heads = [e for e in head_entities if e.text.lower() == head_entity.lower()]
            
            if not matching_heads:
                missing_entities.add(head_entity)
                continue
                
            tail_candidates = self._extract_tail_entities(text, relation_type, head_entity, list(tail_types))
            
            for tail_entity in tail_candidates:
                # Check if tail entity exists in NER results (exact match)
                matching_tails = [e for e in tail_entities if e.text.lower() == tail_entity.lower()]
                
                if not matching_tails:
                    missing_entities.add(tail_entity)
                    continue
                    
                # Validate relation before adding
                head_text = matching_heads[0].text
                tail_text = matching_tails[0].text
                
                # Skip self-referential relations
                if head_text.lower().strip() != tail_text.lower().strip():
                    triples.append(Triple(
                        head=head_text,
                        relation=relation_type,
                        tail=tail_text
                    ))
        
        return triples, missing_entities
    
    def _extract_head_entities(self, text: str, relation_type: str, valid_head_types: List[str]) -> List[str]:
        """
        Step 1: Extract head entities for a given relation type.
        """
        prompts = load_prompts()['knowledge_extraction_expert']
        prompt = prompts['re_head_extraction_prompt'].format(
            relation_type=relation_type,
            valid_head_types=", ".join(valid_head_types),
            text=text
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content.strip()
            
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                data = json.loads(json_repair.repair_json(response_text))
            # Extract all entities from all keys (handles "ANY" type)
            all_entities = []
            for entities in data.values():
                if isinstance(entities, list):
                    all_entities.extend(entities)
            return all_entities
            
        except Exception as e:
            print(f"Error extracting head entities for {relation_type}: {e}")
            return []
    
    def _extract_tail_entities(self, text: str, relation_type: str, head_entity: str, valid_tail_types: List[str]) -> List[str]:
        """
        Step 2: Extract tail entities for a specific head entity and relation.
        """
        prompts = load_prompts()['knowledge_extraction_expert']
        prompt = prompts['re_tail_extraction_prompt'].format(
            head_entity=head_entity,
            relation_type=relation_type,
            valid_tail_types=", ".join(valid_tail_types),
            text=text
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content.strip()
            
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                data = json.loads(json_repair.repair_json(response_text))
            
            # Handle both dict and list responses, always return List[str]
            if isinstance(data, dict):
                # Extract all entities from all keys (handles "ANY" type)
                all_entities = []
                for entities in data.values():
                    if isinstance(entities, list):
                        all_entities.extend(entities)
                return all_entities
            elif isinstance(data, list):
                # Extract strings from list, handling nested structures
                return [str(item) for item in data if isinstance(item, (str, int, float))]
            else:
                return []
            
        except Exception as e:
            print(f"Error extracting tail entities for {relation_type}: {e}")
            return []


class KnowledgeExtractionExpert:
    """
    Main knowledge extraction coordinator that manages NER and RE sub-agents.
    """
    
    def __init__(self, model_name: str = "openai/gpt-3.5-turbo"):
        self.llm = create_openrouter_llm(model_name)
        self.ner_expert = NERExpert(model_name)
        self.re_expert = REExpert(model_name)
        self.prompts = load_prompts()['knowledge_extraction_expert']

    def __call__(self, state: GraphState) -> Dict[str, Any]:
        """
        Main entry point for knowledge extraction.
        Orchestrates NER and RE to extract entities and relations.
        """
        text = state.get("raw_text", "")
        ontology = state.get("ontology")
        
        if not text or not ontology:
            return {
                "error_log": state.get("error_log", []) + [
                    {"error": "Missing text or ontology for extraction"}
                ]
            }
        
        # Step 1: NER pass 
        all_entities = self._extract_all_entities(text, ontology)
        elapsed = get_elapsed_time()
        print_progress(f"[{elapsed:.1f}s] NER completed: {len(all_entities)} entities", final=True)
        
        # Step 2: RE pass 
        all_triples, _ = self._extract_relations_with_feedback(text, all_entities, ontology)
        elapsed = get_elapsed_time()
        print_progress(f"[{elapsed:.1f}s] RE completed: {len(all_triples)} triples", final=True)
        
        # Step 3: Apply internal revision rules
        validated_entities, validated_triples = self._apply_internal_revision(all_entities, all_triples, ontology)
        print(f"\n[REVISION] Validated: {len(validated_entities)}/{len(all_entities)} entities, {len(validated_triples)}/{len(all_triples)} triples")
        
        # Update state with final results
        updates = {
            "extracted_entities": all_entities,
            "initial_triples": all_triples,
            "revised_entities": validated_entities,
            "revised_triples": validated_triples,
            "messages": state.get("messages", []) + [
                {
                    "agent": "knowledge_extraction_expert",
                    "action": "extraction_completed",
                    "entities_extracted": len(validated_entities),
                    "triples_extracted": len(validated_triples)
                }
            ]
        }
        
        return updates
    
    def _extract_all_entities(self, text: str, ontology: FinancialOntology) -> List[Entity]:
        """
        Extracts all entities by iterating through each entity type with reflection revision.
        """
        all_entities = []
        
        for entity_type in ontology.entity_types:
            entities = self.ner_expert.extract_entities_by_type(text, entity_type, ontology)
            all_entities.extend(entities)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in all_entities:
            entity_key = entity.text.lower().strip()
            if entity_key not in seen:
                seen.add(entity_key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _extract_all_relations(self, text: str, entities: List[Entity], 
                              ontology: FinancialOntology) -> List[Triple]:
        """
        Extracts all relations by iterating through each relation type.
        """
        all_triples = []
        
        for relation_type in ontology.relation_types:
            triples = self.re_expert.extract_relations_by_type(text, relation_type, entities, ontology)
            if len(triples) > 0:
                elapsed = get_elapsed_time()
                print_progress(f"[{elapsed:.1f}s] Found {len(triples)} {relation_type} relations")
            all_triples.extend(triples)
        
        # Remove duplicates
        seen = set()
        unique_triples = []
        for triple in all_triples:
            triple_key = (triple.head.lower(), triple.relation, triple.tail.lower())
            if triple_key not in seen:
                seen.add(triple_key)
                unique_triples.append(triple)
        
        return unique_triples
    
    def _extract_relations_with_feedback(self, text: str, entities: List[Entity], 
                                        ontology: FinancialOntology) -> Tuple[List[Triple], Set[str]]:
        """
        Extracts relations with bidirectional feedback to detect missing entities.
        """
        all_triples = []
        all_missing_entities = set()
        
        for i, relation_type in enumerate(ontology.relation_types, 1):
            elapsed = get_elapsed_time()
            print_progress(f"[{elapsed:.1f}s] Processing relation {i}/{len(ontology.relation_types)}: {relation_type}")
            triples, missing_entities = self.re_expert.extract_relations_by_type(
                text, relation_type, entities, ontology
            )
            all_triples.extend(triples)
            all_missing_entities.update(missing_entities)
        
        return all_triples, all_missing_entities
    
    def _apply_internal_revision(self, entities: List[Entity], triples: List[Triple], 
                                ontology: FinancialOntology) -> Tuple[List[Entity], List[Triple]]:
        """
        Applies revision rules internally.
        """
        # Validate entities
        valid_types = set(ontology.entity_types.keys())
        validated_entities = [e for e in entities if e.entity_type in valid_types and e.text.strip()]
        
        # Validate triples with exact entity matching and type constraints
        valid_relations = set(ontology.relation_types.keys())
        
        # Build text->type map from validated entities
        type_by_text = {e.text.lower().strip(): e.entity_type for e in validated_entities}
        
        validated_triples = []
        for triple in triples:
            if triple.relation not in valid_relations:
                continue
            h = triple.head.lower().strip()
            t = triple.tail.lower().strip()
            if h not in type_by_text or t not in type_by_text:
                continue
            rel_sig = ontology.relation_types[triple.relation]   
            if type_by_text[h] not in rel_sig.head_types:
                continue
            if type_by_text[t] not in rel_sig.tail_types:
                continue
            validated_triples.append(triple)
        
        seen = set()
        unique_triples = []
        for tr in validated_triples:
            key = (tr.head.strip().lower(), tr.relation, tr.tail.strip().lower())
            if key not in seen:
                seen.add(key)
                unique_triples.append(tr)
        
        return validated_entities, unique_triples
    
