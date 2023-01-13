export interface TaskInfo {
    id: number;
    name: string;
    started_at: Date;
    is_running: boolean;
    progress: number;
    result: any;
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
    fields?: string[]
}


export interface ExportTweetRequest {
    export_type: string
    id: string
    query: TweetQuery
}