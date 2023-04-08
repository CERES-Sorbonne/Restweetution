export interface TimeWindow {
    start?: String
    end?: String
    recent?: Boolean
}

export interface TaskInfo {
    id: number;
    name: string;
    started_at: Date;
    is_running: boolean;
    progress: number;
    result: any;
    key: string
}

export interface TweetCountQuery{
    date_from?: String
    date_to?: String
    rule_ids?: Array<Number>
}


export interface TweetQuery extends TweetCountQuery {
    ids?: string[]
    offset?: number
    limit?: number
    desc?: boolean
    row_fields?: string[]
    order?: number
}


export interface ExportRequest {
    export_type: string
    id: string
    fields: string[]
    query: ViewQuery
}


export interface ViewResult {
    view: Array<Object>
    fields: Array<string>
    default_fields: Array<string>
}

export interface ViewCountResult {
    tweets?: number
}

export interface CollectionQuery {
    date_from?: String
    date_to?: String
    rule_ids?: Array<Number>
    direct_hit?: Boolean
    limit?: number
    offset?: number
    order?: number
}

export interface CollectionDescription {
    name: string
    isGlobal?: boolean
    rule_ids: number[]
}

export interface ViewQuery {
    collection: CollectionQuery
    view_type: string
}