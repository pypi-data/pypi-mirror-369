from typing import Dict, Any
import json
import re
from langchain_core.messages import HumanMessage
from models import GraphState, FinancialOntology, EntityType, RelationType
from utils import load_prompts, spinner
from utils.llm_factory import create_openrouter_llm

class DomainSpecificExpert:
    def __init__(self, ontology: str = "default"):
        self.llm = None  # Lazy initialization for collaboration
        self.ontology_type = ontology
        self.prompts = load_prompts()['domain_specific_expert']
    
    def __call__(self, state: GraphState) -> Dict[str, Any]:
        # Simple collaboration: pass text for dynamic ontology
        ontology = self._create_domain_ontology(state.get("raw_text", ""))
        return {
            "ontology": ontology,
            "messages": state.get("messages", []) + [{"agent": "domain_specific_expert", "action": "ontology_defined"}]
        }
    
    def _create_domain_ontology(self, text: str = "") -> FinancialOntology:
        if text.strip() and len(text.split()) >= 1:  
            try:
                print(f"\n[ONTOLOGY] Attempting collaboration for text: {len(text)} chars")
                result = self._collaborative_ontology_creation(text)
                print(f"\n[ONTOLOGY] Collaboration succeeded - Dynamic ontology created")
                self._log_ontology(result)
                return result
            except Exception as e:
                print(f"\n[ONTOLOGY] Collaboration failed: {e} - Using static fallback")
        else:
            print(f"\n[ONTOLOGY] Text too short ({len(text.split())} words) - Using static ontology")

        # Fallback to predefined ontology
        return self._get_predefined_ontology(self.ontology_type)
    
    def _get_predefined_ontology(self, ontology: str = "default") -> FinancialOntology:
        """Load static ontology from predefined schema"""
        from config import Config
        
        # Load predefined ontology schema
        ontology_path = Config.get_ontology_file(ontology=ontology)
        with open(ontology_path, 'r') as f:
            ontology_schema = json.load(f)
        
        # Build entity types
        entity_types = {}
        for name, examples in ontology_schema["entities"].items():
            entity_types[name] = EntityType(name=name, examples=examples)
        
        # Build relation types with list constraints (no single-type picking)
        relation_types = {}
        for name, rel_info in ontology_schema["relations"].items():
            relation_types[name] = RelationType(
                name=name,
                head_types=rel_info["head_types"],
                tail_types=rel_info["tail_types"]
            )
        
        return FinancialOntology(entity_types=entity_types, relation_types=relation_types)
    
    def _log_ontology(self, ontology: FinancialOntology):
        """Log the created ontology for debugging"""
        print(f"\n[ONTOLOGY] Entity Types: {list(ontology.entity_types.keys())}")
        print(f"[ONTOLOGY] Relation Types: {list(ontology.relation_types.keys())}")
        # for rel_name, rel_type in ontology.relation_types.items():
        #     print(f"[ONTOLOGY]   {rel_name}: {rel_type.head_types} -> {rel_type.tail_types}")
    
    def get_entity_types_list(self, ontology: FinancialOntology) -> list:
        """Returns a list of entity type names for extraction tasks."""
        return list(ontology.entity_types.keys())
    
    def get_relation_types_list(self, ontology: FinancialOntology) -> list:
        """Returns a list of relation type names for extraction tasks."""
        return list(ontology.relation_types.keys())
    
    def validate_entity_type(self, entity_type: str, ontology: FinancialOntology) -> bool:
        """Validates if an entity type exists in the ontology."""
        return entity_type in ontology.entity_types
    
    def validate_relation_constraints(self, relation: str, head_type: str, tail_type: str, 
                                    ontology: FinancialOntology) -> bool:
        """Validates if a relation satisfies the head/tail type constraints."""
        if relation not in ontology.relation_types:
            return False
        
        rel_type = ontology.relation_types[relation]
        return (head_type in rel_type.head_types and tail_type in rel_type.tail_types)
    
    def _collaborative_ontology_creation(self, text: str) -> FinancialOntology:
        """Domain expert provides ontology based on text analysis"""
        if not self.llm:
            self.llm = create_openrouter_llm()
        
        # Domain Expert provides ontology directly
        ontology_data = self._domain_expert_provide_ontology(text)
        
        return self._build_ontology_from_collaboration(ontology_data)
    
    def _domain_expert_provide_ontology(self, text: str) -> Dict:
        """Domain expert provides ontology based on text analysis"""
        prompt = self.prompts['domain_expert_ontology_prompt']
        
        with spinner("Creating ontology"):
            response = self.llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()
        
        # Remove code fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # First try direct parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print("[DEBUG] Initial JSON parse failed, attempting to clean response...")
            print(f"[DEBUG] Error was: {str(e)}")
            print("[DEBUG] Response preview:")
            print(response_text[:200])  # Show first 200 chars
            
            # Remove trailing commas before } or ]
            cleaned = response_text
            # Fix trailing commas in objects
            cleaned = re.sub(r',(\s*})', r'\1', cleaned)
            # Fix trailing commas in arrays
            cleaned = re.sub(r',(\s*\])', r'\1', cleaned)
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e2:
                print("[DEBUG] Failed to parse even after cleaning. Error:", str(e2))
                raise ValueError("Could not parse LLM response as valid JSON") from e2
    
    def _build_ontology_from_collaboration(self, data: Dict) -> FinancialOntology:
        """Build ontology from predefined schema or fallback to dynamic"""
        try:
            # Use the same predefined schema
            return self._get_predefined_ontology()
            
        except Exception as e:
            print(f"[ONTOLOGY] Failed to load predefined schema: {e} - Using dynamic fallback")
            # Fallback to original dynamic approach
            entity_types = {}
            for name, examples in data.get("entities", {}).items():
                entity_types[name] = EntityType(name=name, examples=examples)
            
            relation_types = {}
            for name, rel_info in data.get("relations", {}).items():
                relation_types[name] = RelationType(
                    name=name,
                    head_type="ANY",
                    tail_type="ANY"
                )
            
            return FinancialOntology(entity_types=entity_types, relation_types=relation_types)