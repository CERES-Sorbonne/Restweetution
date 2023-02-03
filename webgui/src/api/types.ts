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


export interface ExportTweetRequest {
    export_type: string
    id: string
    query: TweetQuery
}