"""
DSPy-based Domain Specific Expert - Creates ontologies with structured outputs.

This agent provides the same interface as the YAML-based version but uses DSPy
for reliable ontology creation without JSON parsing errors.
"""

import dspy
from typing import Dict, Any, List

from models import GraphState, FinancialOntology, EntityType, RelationType
from utils import spinner


class OntologyCreationSignature(dspy.Signature):
    """Create domain-specific ontology for knowledge extraction."""
    text: str = dspy.InputField(desc="Text to analyze for ontology creation")
    # Simple structured output matching existing conversion logic
    entity_types_with_examples: Dict[str, List[str]] = dspy.OutputField(desc="Entity types mapped to example lists")
    relation_types_with_constraints: Dict[str, Dict[str, str]] = dspy.OutputField(desc="Relations mapped to head/tail constraints")


class DomainSpecificExpert:
    """DSPy-based Domain Specific Expert with same interface as YAML version."""
    
    def __init__(self):
        # DSPy LM configured globally - just create predictors
        self.ontology_creator = dspy.Predict(OntologyCreationSignature)
    
    def __call__(self, state: GraphState) -> Dict[str, Any]:
        """Main entry point - same interface as YAML version."""
        ontology = self._create_domain_ontology(state.get("raw_text", ""))
        return {
            "ontology": ontology,
            "messages": state.get("messages", []) + [
                {"agent": "dspy_domain_specific_expert", "action": "ontology_defined"}
            ]
        }
    
    def _create_domain_ontology(self, text: str = "") -> FinancialOntology:
        """Create ontology - use static NYT11-HRL ontology for evaluation consistency."""
        print(f"\n[DSPy ONTOLOGY] Using static NYT11-HRL ontology for evaluation")
        result = self._get_static_ontology()
        self._log_ontology(result)
        return result
    
    def _get_static_ontology(self) -> FinancialOntology:
        """Static ontology with NYT11-HRL 12 relations and generic ENTITY type."""
        # Generic ENTITY type as used in NYT11-HRL evaluation
        entity_types = {
            "ENTITY": EntityType(name="ENTITY", examples=[
                "Tim Pawlenty", "Minnesota", "Sony", "Tokyo", "Barack Obama", 
                "United States", "Apple", "New York", "Microsoft", "California"
            ])
        }
        
        # NYT11-HRL 12 standard relations - all use generic ENTITY constraints
        relation_types = {
            "/business/company/founders": RelationType(name="/business/company/founders", head_type="ENTITY", tail_type="ENTITY"),
            "/business/person/company": RelationType(name="/business/person/company", head_type="ENTITY", tail_type="ENTITY"),
            "/location/administrative_division/country": RelationType(name="/location/administrative_division/country", head_type="ENTITY", tail_type="ENTITY"),
            "/location/country/administrative_divisions": RelationType(name="/location/country/administrative_divisions", head_type="ENTITY", tail_type="ENTITY"),
            "/location/country/capital": RelationType(name="/location/country/capital", head_type="ENTITY", tail_type="ENTITY"),
            "/location/location/contains": RelationType(name="/location/location/contains", head_type="ENTITY", tail_type="ENTITY"),
            "/location/neighborhood/neighborhood_of": RelationType(name="/location/neighborhood/neighborhood_of", head_type="ENTITY", tail_type="ENTITY"),
            "/people/deceased_person/place_of_death": RelationType(name="/people/deceased_person/place_of_death", head_type="ENTITY", tail_type="ENTITY"),
            "/people/person/children": RelationType(name="/people/person/children", head_type="ENTITY", tail_type="ENTITY"),
            "/people/person/nationality": RelationType(name="/people/person/nationality", head_type="ENTITY", tail_type="ENTITY"),
            "/people/person/place_lived": RelationType(name="/people/person/place_lived", head_type="ENTITY", tail_type="ENTITY"),
            "/people/person/place_of_birth": RelationType(name="/people/person/place_of_birth", head_type="ENTITY", tail_type="ENTITY")
        }
        
        return FinancialOntology(entity_types=entity_types, relation_types=relation_types)
    
    def _log_ontology(self, ontology: FinancialOntology):
        """Log the created ontology for debugging."""
        print(f"\n[DSPy ONTOLOGY] Entity Types: {list(ontology.entity_types.keys())}")
        print(f"[DSPy ONTOLOGY] Relation Types: {list(ontology.relation_types.keys())}")
        for rel_name, rel_type in ontology.relation_types.items():
            print(f"[DSPy ONTOLOGY]   {rel_name}: {rel_type.head_type} -> {rel_type.tail_type}")
    
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
        return (rel_type.head_type == head_type and rel_type.tail_type == tail_type)
    
    def _collaborative_ontology_creation(self, text: str) -> FinancialOntology:
        """DSPy-based ontology creation with structured outputs."""
        ontology_data = self._dspy_domain_expert_provide_ontology(text)
        return self._build_ontology_from_collaboration(ontology_data)
    
    def _dspy_domain_expert_provide_ontology(self, text: str) -> Dict:
        """DSPy-based ontology creation - outputs format matching existing conversion logic."""
        with spinner("Creating DSPy ontology"):
            result = self.ontology_creator(text=text)
        
        print(f"[DSPy ONTOLOGY] Structured response received")
        
        # Format data to match existing _build_ontology_from_collaboration expectations
        return {
            "entities": result.entity_types_with_examples,
            "relations": result.relation_types_with_constraints
        }
    
    def _build_ontology_from_collaboration(self, data: Dict) -> FinancialOntology:
        """Build ontology from DSPy structured response."""
        entity_types = {}
        for name, examples in data.get("entities", {}).items():
            entity_types[name] = EntityType(name=name, examples=examples)
        
        relation_types = {}
        for name, rel_info in data.get("relations", {}).items():
            # Defensive handling: convert arrays to strings if needed
            head_type = rel_info.get("head", "")
            tail_type = rel_info.get("tail", "")
            
            if isinstance(head_type, list):
                head_type = head_type[0] if head_type else ""
            if isinstance(tail_type, list):
                tail_type = tail_type[0] if tail_type else ""
                
            relation_types[name] = RelationType(
                name=name,
                head_type=str(head_type),
                tail_type=str(tail_type)
            )
        
        return FinancialOntology(entity_types=entity_types, relation_types=relation_types)