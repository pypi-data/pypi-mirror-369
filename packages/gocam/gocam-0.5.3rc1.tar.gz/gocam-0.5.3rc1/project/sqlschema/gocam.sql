-- # Class: Model Description: A model of a biological program consisting of a set of causally connected activities.
--     * Slot: id Description: The identifier of the model. Should be in gocam namespace.
--     * Slot: title Description: The human-readable descriptive title of the model
--     * Slot: taxon Description: The primary taxon that the model is about
--     * Slot: status Description: The status of the model in terms of its progression along the developmental lifecycle
--     * Slot: query_index_id Description: An optional object that contains the results of indexing a model with various summary statistics and retrieval indices.
-- # Class: Activity Description: An individual activity in a causal model, representing the individual molecular activity of a single gene product or complex in the context of a particular model
--     * Slot: id Description: Identifier of the activity unit. Should be in gocam namespace.
--     * Slot: Model_id Description: Autocreated FK slot
--     * Slot: enabled_by_id Description: The gene product or complex that carries out the activity
--     * Slot: molecular_function_id Description: The molecular function that is carried out by the gene product or complex
--     * Slot: occurs_in_id Description: The cellular location in which the activity occurs
--     * Slot: part_of_id Description: The larger biological process in which the activity is a part
--     * Slot: has_primary_input_id Description: The primary input molecule that is directly consumed by the activity
--     * Slot: has_primary_output_id Description: The primary output molecule that is directly produced by the activity
-- # Class: EvidenceItem Description: An individual piece of evidence that is associated with an assertion in a model
--     * Slot: id
--     * Slot: term Description: The ECO term representing the type of evidence
--     * Slot: reference Description: The publication of reference that describes the evidence
--     * Slot: Association_id Description: Autocreated FK slot
--     * Slot: EnabledByAssociation_id Description: Autocreated FK slot
--     * Slot: EnabledByGeneProductAssociation_id Description: Autocreated FK slot
--     * Slot: EnabledByProteinComplexAssociation_id Description: Autocreated FK slot
--     * Slot: CausalAssociation_id Description: Autocreated FK slot
--     * Slot: TermAssociation_id Description: Autocreated FK slot
--     * Slot: MolecularFunctionAssociation_id Description: Autocreated FK slot
--     * Slot: BiologicalProcessAssociation_id Description: Autocreated FK slot
--     * Slot: CellularAnatomicalEntityAssociation_id Description: Autocreated FK slot
--     * Slot: CellTypeAssociation_id Description: Autocreated FK slot
--     * Slot: GrossAnatomyAssociation_id Description: Autocreated FK slot
--     * Slot: MoleculeAssociation_id Description: Autocreated FK slot
-- # Abstract Class: Association Description: An abstract grouping for different kinds of evidence-associated provenance
--     * Slot: id
--     * Slot: type Description: The type of association.
-- # Abstract Class: EnabledByAssociation Description: An association between an activity and the gene product or complex or set of potential gene products  that carry out that activity.
--     * Slot: id
--     * Slot: term Description: The gene product or complex that carries out the activity
--     * Slot: type Description: The type of association.
-- # Class: EnabledByGeneProductAssociation Description: An association between an activity and an individual gene product
--     * Slot: id
--     * Slot: term Description: A "term" that is an entity database object representing an individual gene product.
--     * Slot: type Description: The type of association.
-- # Class: EnabledByProteinComplexAssociation Description: An association between an activity and a protein complex, where the complex carries out the activity. This should only be used when the activity cannot be attributed to an individual member of the complex, but instead the function is an emergent property of the complex.
--     * Slot: id
--     * Slot: term Description: The gene product or complex that carries out the activity
--     * Slot: type Description: The type of association.
-- # Class: CausalAssociation Description: A causal association between two activities
--     * Slot: id
--     * Slot: predicate Description: The RO relation that represents the type of relationship
--     * Slot: downstream_activity Description: The activity unit that is downstream of this one
--     * Slot: type Description: The type of association.
--     * Slot: Activity_id Description: Autocreated FK slot
-- # Abstract Class: TermAssociation Description: An association between an activity and a term, potentially with extensions. This is an abstract class for grouping purposes, it should not be directly instantiated, instead a subclass should be instantiated.
--     * Slot: id
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
-- # Class: MolecularFunctionAssociation Description: An association between an activity and a molecular function term
--     * Slot: id
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
-- # Class: BiologicalProcessAssociation Description: An association between an activity and a biological process term
--     * Slot: id
--     * Slot: happens_during Description: Optional extension describing where the BP takes place
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
--     * Slot: part_of_id Description: Optional extension allowing hierarchical nesting of BPs
-- # Class: CellularAnatomicalEntityAssociation Description: An association between an activity and a cellular anatomical entity term
--     * Slot: id
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
--     * Slot: part_of_id Description: Optional extension allowing hierarchical nesting of CCs
-- # Class: CellTypeAssociation Description: An association between an activity and a cell type term
--     * Slot: id
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
--     * Slot: part_of_id
-- # Class: GrossAnatomyAssociation Description: An association between an activity and a gross anatomical structure term
--     * Slot: id
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
--     * Slot: part_of_id
-- # Class: MoleculeAssociation Description: An association between an activity and a molecule term
--     * Slot: id
--     * Slot: term Description: The ontology term that describes the nature of the association
--     * Slot: type Description: The type of association.
--     * Slot: Activity_id Description: Autocreated FK slot
-- # Class: Object Description: An abstract class for all identified objects in a model
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
--     * Slot: Model_id Description: Autocreated FK slot
-- # Abstract Class: TermObject Description: An abstract class for all ontology term objects
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
--     * Slot: QueryIndex_id Description: Autocreated FK slot
-- # Class: PublicationObject Description: An object that represents a publication or other kind of reference
--     * Slot: abstract_text
--     * Slot: full_text
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
--     * Slot: QueryIndex_id Description: Autocreated FK slot
-- # Class: EvidenceTermObject Description: A term object that represents an evidence term from ECO. Only ECO terms that map up to a GO GAF evidence code should be used.
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: MolecularFunctionTermObject Description: A term object that represents a molecular function term from GO
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: BiologicalProcessTermObject Description: A term object that represents a biological process term from GO
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: CellularAnatomicalEntityTermObject Description: A term object that represents a cellular anatomical entity term from GO
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: MoleculeTermObject Description: A term object that represents a molecule term from CHEBI or UniProtKB
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: CellTypeTermObject Description: A term object that represents a cell type term from CL
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: GrossAnatomicalStructureTermObject Description: A term object that represents a gross anatomical structure term from UBERON
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: PhaseTermObject Description: A term object that represents a phase term from GO or UBERON
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Abstract Class: InformationBiomacromoleculeTermObject Description: An abstract class for all information biomacromolecule term objects
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: GeneProductTermObject Description: A term object that represents a gene product term from GO or UniProtKB
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: ProteinComplexTermObject Description: A term object that represents a protein complex term from GO
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: TaxonTermObject Description: A term object that represents a taxon term from NCBITaxon
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: PredicateTermObject Description: A term object that represents a taxon term from NCBITaxon
--     * Slot: id
--     * Slot: label
--     * Slot: type
--     * Slot: obsolete
-- # Class: ProvenanceInfo Description: Provenance information for an object
--     * Slot: id
--     * Slot: created
--     * Slot: date
--     * Slot: Model_id Description: Autocreated FK slot
--     * Slot: Activity_id Description: Autocreated FK slot
--     * Slot: EvidenceItem_id Description: Autocreated FK slot
--     * Slot: Association_id Description: Autocreated FK slot
--     * Slot: EnabledByAssociation_id Description: Autocreated FK slot
--     * Slot: EnabledByGeneProductAssociation_id Description: Autocreated FK slot
--     * Slot: EnabledByProteinComplexAssociation_id Description: Autocreated FK slot
--     * Slot: CausalAssociation_id Description: Autocreated FK slot
--     * Slot: TermAssociation_id Description: Autocreated FK slot
--     * Slot: MolecularFunctionAssociation_id Description: Autocreated FK slot
--     * Slot: BiologicalProcessAssociation_id Description: Autocreated FK slot
--     * Slot: CellularAnatomicalEntityAssociation_id Description: Autocreated FK slot
--     * Slot: CellTypeAssociation_id Description: Autocreated FK slot
--     * Slot: GrossAnatomyAssociation_id Description: Autocreated FK slot
--     * Slot: MoleculeAssociation_id Description: Autocreated FK slot
-- # Class: QueryIndex Description: An index that is optionally placed on a model in order to support common query or index operations. Note that this index is not typically populated in the working transactional store for a model, it is derived via computation from core primary model information.
--     * Slot: id
--     * Slot: number_of_activities Description: The number of activities in a model.
--     * Slot: number_of_enabled_by_terms Description: The number of molecular entities or sets of entities in a model.
--     * Slot: number_of_causal_associations Description: Total number of causal association edges connecting activities in a model.
--     * Slot: length_of_longest_causal_association_path Description: The maximum number of hops along activities along the direction of causal flow in a model.
--     * Slot: number_of_strongly_connected_components Description: The number of distinct components that consist of activities that are connected (directly or indirectly) via causal connections. Most models will consist of a single SCC. Some models may consist of two or more "islands" where there is no connection from one island to another.
--     * Slot: number_of_start_activities Description: The number of start activities in a model
--     * Slot: number_of_end_activities Description: The number of end activities in a model
--     * Slot: number_of_intermediate_activities Description: The number of intermediate activities in a model
--     * Slot: number_of_singleton_activities Description: The number of singleton activities in a model
-- # Class: Model_additional_taxa
--     * Slot: Model_id Description: Autocreated FK slot
--     * Slot: additional_taxa_id Description: Additional taxa that the model is about
-- # Class: Model_comments
--     * Slot: Model_id Description: Autocreated FK slot
--     * Slot: comments Description: Curator-provided comments about the model
-- # Class: EvidenceItem_with_objects
--     * Slot: EvidenceItem_id Description: Autocreated FK slot
--     * Slot: with_objects_id Description: Supporting database entities or terms
-- # Class: EnabledByProteinComplexAssociation_members
--     * Slot: EnabledByProteinComplexAssociation_id Description: Autocreated FK slot
--     * Slot: members_id Description: The gene products that are part of the complex
-- # Class: ProvenanceInfo_contributor
--     * Slot: ProvenanceInfo_id Description: Autocreated FK slot
--     * Slot: contributor
-- # Class: ProvenanceInfo_provided_by
--     * Slot: ProvenanceInfo_id Description: Autocreated FK slot
--     * Slot: provided_by
-- # Class: QueryIndex_start_activities
--     * Slot: QueryIndex_id Description: Autocreated FK slot
--     * Slot: start_activities_id Description: The set of activities that are the starting points of the model, i.e. those that have no incoming causal associations.
-- # Class: QueryIndex_end_activities
--     * Slot: QueryIndex_id Description: Autocreated FK slot
--     * Slot: end_activities_id Description: The set of activities that are the end points of the model, i.e. those that have no outgoing causal associations.
-- # Class: QueryIndex_intermediate_activities
--     * Slot: QueryIndex_id Description: Autocreated FK slot
--     * Slot: intermediate_activities_id Description: The set of activities that are neither start nor end activities, i.e. those that have both incoming and outgoing causal associations.
-- # Class: QueryIndex_singleton_activities
--     * Slot: QueryIndex_id Description: Autocreated FK slot
--     * Slot: singleton_activities_id Description: The set of activities that have no causal associations, i.e. those that are not connected to any other activity in the model.

CREATE TABLE "Activity" (
	id TEXT NOT NULL,
	"Model_id" TEXT,
	enabled_by_id INTEGER,
	molecular_function_id INTEGER,
	occurs_in_id INTEGER,
	part_of_id INTEGER,
	has_primary_input_id INTEGER,
	has_primary_output_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY("Model_id") REFERENCES "Model" (id),
	FOREIGN KEY(enabled_by_id) REFERENCES "EnabledByAssociation" (id),
	FOREIGN KEY(molecular_function_id) REFERENCES "MolecularFunctionAssociation" (id),
	FOREIGN KEY(occurs_in_id) REFERENCES "CellularAnatomicalEntityAssociation" (id),
	FOREIGN KEY(part_of_id) REFERENCES "BiologicalProcessAssociation" (id),
	FOREIGN KEY(has_primary_input_id) REFERENCES "MoleculeAssociation" (id),
	FOREIGN KEY(has_primary_output_id) REFERENCES "MoleculeAssociation" (id)
);CREATE INDEX "ix_Activity_id" ON "Activity" (id);
CREATE TABLE "Association" (
	id INTEGER NOT NULL,
	type TEXT,
	PRIMARY KEY (id)
);CREATE INDEX "ix_Association_id" ON "Association" (id);
CREATE TABLE "MoleculeAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	"Activity_id" TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "MoleculeTermObject" (id),
	FOREIGN KEY("Activity_id") REFERENCES "Activity" (id)
);CREATE INDEX "ix_MoleculeAssociation_id" ON "MoleculeAssociation" (id);
CREATE TABLE "EvidenceTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_EvidenceTermObject_id" ON "EvidenceTermObject" (id);
CREATE TABLE "MolecularFunctionTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_MolecularFunctionTermObject_id" ON "MolecularFunctionTermObject" (id);
CREATE TABLE "BiologicalProcessTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_BiologicalProcessTermObject_id" ON "BiologicalProcessTermObject" (id);
CREATE TABLE "CellularAnatomicalEntityTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_CellularAnatomicalEntityTermObject_id" ON "CellularAnatomicalEntityTermObject" (id);
CREATE TABLE "MoleculeTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_MoleculeTermObject_id" ON "MoleculeTermObject" (id);
CREATE TABLE "CellTypeTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_CellTypeTermObject_id" ON "CellTypeTermObject" (id);
CREATE TABLE "GrossAnatomicalStructureTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_GrossAnatomicalStructureTermObject_id" ON "GrossAnatomicalStructureTermObject" (id);
CREATE TABLE "PhaseTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_PhaseTermObject_id" ON "PhaseTermObject" (id);
CREATE TABLE "InformationBiomacromoleculeTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_InformationBiomacromoleculeTermObject_id" ON "InformationBiomacromoleculeTermObject" (id);
CREATE TABLE "GeneProductTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_GeneProductTermObject_id" ON "GeneProductTermObject" (id);
CREATE TABLE "ProteinComplexTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_ProteinComplexTermObject_id" ON "ProteinComplexTermObject" (id);
CREATE TABLE "TaxonTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_TaxonTermObject_id" ON "TaxonTermObject" (id);
CREATE TABLE "PredicateTermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	PRIMARY KEY (id)
);CREATE INDEX "ix_PredicateTermObject_id" ON "PredicateTermObject" (id);
CREATE TABLE "QueryIndex" (
	id INTEGER NOT NULL,
	number_of_activities INTEGER,
	number_of_enabled_by_terms INTEGER,
	number_of_causal_associations INTEGER,
	length_of_longest_causal_association_path INTEGER,
	number_of_strongly_connected_components INTEGER,
	number_of_start_activities INTEGER,
	number_of_end_activities INTEGER,
	number_of_intermediate_activities INTEGER,
	number_of_singleton_activities INTEGER,
	PRIMARY KEY (id)
);CREATE INDEX "ix_QueryIndex_id" ON "QueryIndex" (id);
CREATE TABLE "Model" (
	id TEXT NOT NULL,
	title TEXT NOT NULL,
	taxon TEXT,
	status VARCHAR(13),
	query_index_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(taxon) REFERENCES "TaxonTermObject" (id),
	FOREIGN KEY(query_index_id) REFERENCES "QueryIndex" (id)
);CREATE INDEX "ix_Model_id" ON "Model" (id);
CREATE TABLE "EnabledByAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "InformationBiomacromoleculeTermObject" (id)
);CREATE INDEX "ix_EnabledByAssociation_id" ON "EnabledByAssociation" (id);
CREATE TABLE "EnabledByGeneProductAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "GeneProductTermObject" (id)
);CREATE INDEX "ix_EnabledByGeneProductAssociation_id" ON "EnabledByGeneProductAssociation" (id);
CREATE TABLE "EnabledByProteinComplexAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "ProteinComplexTermObject" (id)
);CREATE INDEX "ix_EnabledByProteinComplexAssociation_id" ON "EnabledByProteinComplexAssociation" (id);
CREATE TABLE "CausalAssociation" (
	id INTEGER NOT NULL,
	predicate TEXT,
	downstream_activity TEXT,
	type TEXT,
	"Activity_id" TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(predicate) REFERENCES "PredicateTermObject" (id),
	FOREIGN KEY(downstream_activity) REFERENCES "Activity" (id),
	FOREIGN KEY("Activity_id") REFERENCES "Activity" (id)
);CREATE INDEX "ix_CausalAssociation_id" ON "CausalAssociation" (id);
CREATE TABLE "MolecularFunctionAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "MolecularFunctionTermObject" (id)
);CREATE INDEX "ix_MolecularFunctionAssociation_id" ON "MolecularFunctionAssociation" (id);
CREATE TABLE "BiologicalProcessAssociation" (
	id INTEGER NOT NULL,
	happens_during TEXT,
	term TEXT,
	type TEXT,
	part_of_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(happens_during) REFERENCES "PhaseTermObject" (id),
	FOREIGN KEY(term) REFERENCES "BiologicalProcessTermObject" (id),
	FOREIGN KEY(part_of_id) REFERENCES "BiologicalProcessAssociation" (id)
);CREATE INDEX "ix_BiologicalProcessAssociation_id" ON "BiologicalProcessAssociation" (id);
CREATE TABLE "GrossAnatomyAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	part_of_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "GrossAnatomicalStructureTermObject" (id),
	FOREIGN KEY(part_of_id) REFERENCES "GrossAnatomyAssociation" (id)
);CREATE INDEX "ix_GrossAnatomyAssociation_id" ON "GrossAnatomyAssociation" (id);
CREATE TABLE "TermObject" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	"QueryIndex_id" INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY("QueryIndex_id") REFERENCES "QueryIndex" (id)
);CREATE INDEX "ix_TermObject_id" ON "TermObject" (id);
CREATE TABLE "PublicationObject" (
	abstract_text TEXT,
	full_text TEXT,
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	"QueryIndex_id" INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY("QueryIndex_id") REFERENCES "QueryIndex" (id)
);CREATE INDEX "ix_PublicationObject_id" ON "PublicationObject" (id);
CREATE TABLE "QueryIndex_start_activities" (
	"QueryIndex_id" INTEGER,
	start_activities_id TEXT,
	PRIMARY KEY ("QueryIndex_id", start_activities_id),
	FOREIGN KEY("QueryIndex_id") REFERENCES "QueryIndex" (id),
	FOREIGN KEY(start_activities_id) REFERENCES "Activity" (id)
);CREATE INDEX "ix_QueryIndex_start_activities_QueryIndex_id" ON "QueryIndex_start_activities" ("QueryIndex_id");CREATE INDEX "ix_QueryIndex_start_activities_start_activities_id" ON "QueryIndex_start_activities" (start_activities_id);
CREATE TABLE "QueryIndex_end_activities" (
	"QueryIndex_id" INTEGER,
	end_activities_id TEXT,
	PRIMARY KEY ("QueryIndex_id", end_activities_id),
	FOREIGN KEY("QueryIndex_id") REFERENCES "QueryIndex" (id),
	FOREIGN KEY(end_activities_id) REFERENCES "Activity" (id)
);CREATE INDEX "ix_QueryIndex_end_activities_QueryIndex_id" ON "QueryIndex_end_activities" ("QueryIndex_id");CREATE INDEX "ix_QueryIndex_end_activities_end_activities_id" ON "QueryIndex_end_activities" (end_activities_id);
CREATE TABLE "QueryIndex_intermediate_activities" (
	"QueryIndex_id" INTEGER,
	intermediate_activities_id TEXT,
	PRIMARY KEY ("QueryIndex_id", intermediate_activities_id),
	FOREIGN KEY("QueryIndex_id") REFERENCES "QueryIndex" (id),
	FOREIGN KEY(intermediate_activities_id) REFERENCES "Activity" (id)
);CREATE INDEX "ix_QueryIndex_intermediate_activities_QueryIndex_id" ON "QueryIndex_intermediate_activities" ("QueryIndex_id");CREATE INDEX "ix_QueryIndex_intermediate_activities_intermediate_activities_id" ON "QueryIndex_intermediate_activities" (intermediate_activities_id);
CREATE TABLE "QueryIndex_singleton_activities" (
	"QueryIndex_id" INTEGER,
	singleton_activities_id TEXT,
	PRIMARY KEY ("QueryIndex_id", singleton_activities_id),
	FOREIGN KEY("QueryIndex_id") REFERENCES "QueryIndex" (id),
	FOREIGN KEY(singleton_activities_id) REFERENCES "Activity" (id)
);CREATE INDEX "ix_QueryIndex_singleton_activities_singleton_activities_id" ON "QueryIndex_singleton_activities" (singleton_activities_id);CREATE INDEX "ix_QueryIndex_singleton_activities_QueryIndex_id" ON "QueryIndex_singleton_activities" ("QueryIndex_id");
CREATE TABLE "TermAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "TermObject" (id)
);CREATE INDEX "ix_TermAssociation_id" ON "TermAssociation" (id);
CREATE TABLE "CellTypeAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	part_of_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "CellTypeTermObject" (id),
	FOREIGN KEY(part_of_id) REFERENCES "GrossAnatomyAssociation" (id)
);CREATE INDEX "ix_CellTypeAssociation_id" ON "CellTypeAssociation" (id);
CREATE TABLE "Object" (
	id TEXT NOT NULL,
	label TEXT,
	type TEXT,
	obsolete BOOLEAN,
	"Model_id" TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY("Model_id") REFERENCES "Model" (id)
);CREATE INDEX "ix_Object_id" ON "Object" (id);
CREATE TABLE "Model_additional_taxa" (
	"Model_id" TEXT,
	additional_taxa_id TEXT,
	PRIMARY KEY ("Model_id", additional_taxa_id),
	FOREIGN KEY("Model_id") REFERENCES "Model" (id),
	FOREIGN KEY(additional_taxa_id) REFERENCES "TaxonTermObject" (id)
);CREATE INDEX "ix_Model_additional_taxa_Model_id" ON "Model_additional_taxa" ("Model_id");CREATE INDEX "ix_Model_additional_taxa_additional_taxa_id" ON "Model_additional_taxa" (additional_taxa_id);
CREATE TABLE "Model_comments" (
	"Model_id" TEXT,
	comments TEXT,
	PRIMARY KEY ("Model_id", comments),
	FOREIGN KEY("Model_id") REFERENCES "Model" (id)
);CREATE INDEX "ix_Model_comments_comments" ON "Model_comments" (comments);CREATE INDEX "ix_Model_comments_Model_id" ON "Model_comments" ("Model_id");
CREATE TABLE "EnabledByProteinComplexAssociation_members" (
	"EnabledByProteinComplexAssociation_id" INTEGER,
	members_id TEXT,
	PRIMARY KEY ("EnabledByProteinComplexAssociation_id", members_id),
	FOREIGN KEY("EnabledByProteinComplexAssociation_id") REFERENCES "EnabledByProteinComplexAssociation" (id),
	FOREIGN KEY(members_id) REFERENCES "GeneProductTermObject" (id)
);CREATE INDEX "ix_EnabledByProteinComplexAssociation_members_members_id" ON "EnabledByProteinComplexAssociation_members" (members_id);CREATE INDEX "ix_EnabledByProteinComplexAssociation_members_EnabledByProteinComplexAssociation_id" ON "EnabledByProteinComplexAssociation_members" ("EnabledByProteinComplexAssociation_id");
CREATE TABLE "CellularAnatomicalEntityAssociation" (
	id INTEGER NOT NULL,
	term TEXT,
	type TEXT,
	part_of_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "CellularAnatomicalEntityTermObject" (id),
	FOREIGN KEY(part_of_id) REFERENCES "CellTypeAssociation" (id)
);CREATE INDEX "ix_CellularAnatomicalEntityAssociation_id" ON "CellularAnatomicalEntityAssociation" (id);
CREATE TABLE "EvidenceItem" (
	id INTEGER NOT NULL,
	term TEXT,
	reference TEXT,
	"Association_id" INTEGER,
	"EnabledByAssociation_id" INTEGER,
	"EnabledByGeneProductAssociation_id" INTEGER,
	"EnabledByProteinComplexAssociation_id" INTEGER,
	"CausalAssociation_id" INTEGER,
	"TermAssociation_id" INTEGER,
	"MolecularFunctionAssociation_id" INTEGER,
	"BiologicalProcessAssociation_id" INTEGER,
	"CellularAnatomicalEntityAssociation_id" INTEGER,
	"CellTypeAssociation_id" INTEGER,
	"GrossAnatomyAssociation_id" INTEGER,
	"MoleculeAssociation_id" INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(term) REFERENCES "EvidenceTermObject" (id),
	FOREIGN KEY(reference) REFERENCES "PublicationObject" (id),
	FOREIGN KEY("Association_id") REFERENCES "Association" (id),
	FOREIGN KEY("EnabledByAssociation_id") REFERENCES "EnabledByAssociation" (id),
	FOREIGN KEY("EnabledByGeneProductAssociation_id") REFERENCES "EnabledByGeneProductAssociation" (id),
	FOREIGN KEY("EnabledByProteinComplexAssociation_id") REFERENCES "EnabledByProteinComplexAssociation" (id),
	FOREIGN KEY("CausalAssociation_id") REFERENCES "CausalAssociation" (id),
	FOREIGN KEY("TermAssociation_id") REFERENCES "TermAssociation" (id),
	FOREIGN KEY("MolecularFunctionAssociation_id") REFERENCES "MolecularFunctionAssociation" (id),
	FOREIGN KEY("BiologicalProcessAssociation_id") REFERENCES "BiologicalProcessAssociation" (id),
	FOREIGN KEY("CellularAnatomicalEntityAssociation_id") REFERENCES "CellularAnatomicalEntityAssociation" (id),
	FOREIGN KEY("CellTypeAssociation_id") REFERENCES "CellTypeAssociation" (id),
	FOREIGN KEY("GrossAnatomyAssociation_id") REFERENCES "GrossAnatomyAssociation" (id),
	FOREIGN KEY("MoleculeAssociation_id") REFERENCES "MoleculeAssociation" (id)
);CREATE INDEX "ix_EvidenceItem_id" ON "EvidenceItem" (id);
CREATE TABLE "ProvenanceInfo" (
	id INTEGER NOT NULL,
	created TEXT,
	date TEXT,
	"Model_id" TEXT,
	"Activity_id" TEXT,
	"EvidenceItem_id" INTEGER,
	"Association_id" INTEGER,
	"EnabledByAssociation_id" INTEGER,
	"EnabledByGeneProductAssociation_id" INTEGER,
	"EnabledByProteinComplexAssociation_id" INTEGER,
	"CausalAssociation_id" INTEGER,
	"TermAssociation_id" INTEGER,
	"MolecularFunctionAssociation_id" INTEGER,
	"BiologicalProcessAssociation_id" INTEGER,
	"CellularAnatomicalEntityAssociation_id" INTEGER,
	"CellTypeAssociation_id" INTEGER,
	"GrossAnatomyAssociation_id" INTEGER,
	"MoleculeAssociation_id" INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY("Model_id") REFERENCES "Model" (id),
	FOREIGN KEY("Activity_id") REFERENCES "Activity" (id),
	FOREIGN KEY("EvidenceItem_id") REFERENCES "EvidenceItem" (id),
	FOREIGN KEY("Association_id") REFERENCES "Association" (id),
	FOREIGN KEY("EnabledByAssociation_id") REFERENCES "EnabledByAssociation" (id),
	FOREIGN KEY("EnabledByGeneProductAssociation_id") REFERENCES "EnabledByGeneProductAssociation" (id),
	FOREIGN KEY("EnabledByProteinComplexAssociation_id") REFERENCES "EnabledByProteinComplexAssociation" (id),
	FOREIGN KEY("CausalAssociation_id") REFERENCES "CausalAssociation" (id),
	FOREIGN KEY("TermAssociation_id") REFERENCES "TermAssociation" (id),
	FOREIGN KEY("MolecularFunctionAssociation_id") REFERENCES "MolecularFunctionAssociation" (id),
	FOREIGN KEY("BiologicalProcessAssociation_id") REFERENCES "BiologicalProcessAssociation" (id),
	FOREIGN KEY("CellularAnatomicalEntityAssociation_id") REFERENCES "CellularAnatomicalEntityAssociation" (id),
	FOREIGN KEY("CellTypeAssociation_id") REFERENCES "CellTypeAssociation" (id),
	FOREIGN KEY("GrossAnatomyAssociation_id") REFERENCES "GrossAnatomyAssociation" (id),
	FOREIGN KEY("MoleculeAssociation_id") REFERENCES "MoleculeAssociation" (id)
);CREATE INDEX "ix_ProvenanceInfo_id" ON "ProvenanceInfo" (id);
CREATE TABLE "EvidenceItem_with_objects" (
	"EvidenceItem_id" INTEGER,
	with_objects_id TEXT,
	PRIMARY KEY ("EvidenceItem_id", with_objects_id),
	FOREIGN KEY("EvidenceItem_id") REFERENCES "EvidenceItem" (id),
	FOREIGN KEY(with_objects_id) REFERENCES "Object" (id)
);CREATE INDEX "ix_EvidenceItem_with_objects_with_objects_id" ON "EvidenceItem_with_objects" (with_objects_id);CREATE INDEX "ix_EvidenceItem_with_objects_EvidenceItem_id" ON "EvidenceItem_with_objects" ("EvidenceItem_id");
CREATE TABLE "ProvenanceInfo_contributor" (
	"ProvenanceInfo_id" INTEGER,
	contributor TEXT,
	PRIMARY KEY ("ProvenanceInfo_id", contributor),
	FOREIGN KEY("ProvenanceInfo_id") REFERENCES "ProvenanceInfo" (id)
);CREATE INDEX "ix_ProvenanceInfo_contributor_contributor" ON "ProvenanceInfo_contributor" (contributor);CREATE INDEX "ix_ProvenanceInfo_contributor_ProvenanceInfo_id" ON "ProvenanceInfo_contributor" ("ProvenanceInfo_id");
CREATE TABLE "ProvenanceInfo_provided_by" (
	"ProvenanceInfo_id" INTEGER,
	provided_by TEXT,
	PRIMARY KEY ("ProvenanceInfo_id", provided_by),
	FOREIGN KEY("ProvenanceInfo_id") REFERENCES "ProvenanceInfo" (id)
);CREATE INDEX "ix_ProvenanceInfo_provided_by_provided_by" ON "ProvenanceInfo_provided_by" (provided_by);CREATE INDEX "ix_ProvenanceInfo_provided_by_ProvenanceInfo_id" ON "ProvenanceInfo_provided_by" ("ProvenanceInfo_id");
