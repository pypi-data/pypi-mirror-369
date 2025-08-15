export interface Position {
  x: number;
  y: number;
}

export interface GraphicalObject {
  position: Position;
}

export interface ReferenceObject {
  address: string;
}

export interface Property {
  name: string;
  referenceObject?: ReferenceObject;
  valueType?: string;
  value?: number | string;
}

export interface SimulatorObjectNode {
  id: string;
  name: string;
  type: string;
  graphicalObject?: GraphicalObject;
  properties?: Property[];
}

export interface SimulatorObjectEdge {
  id: string;
  source: string;
  target: string;
  sourcePort?: string;
  targetPort?: string;
}

export interface Flowsheet {
  simulatorObjectNodes: SimulatorObjectNode[];
  simulatorObjectEdges: SimulatorObjectEdge[];
}

export interface FlowsheetItem {
  dataSetId?: number;
  modelRevisionExternalId?: string;
  flowsheet: Flowsheet;
}

export interface FlowsheetData {
  items: FlowsheetItem[];
}