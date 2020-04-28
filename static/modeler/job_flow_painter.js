export class JobFlowPainter {
    constructor(options) {
        options = options || {
            height: 800,
            width: 1000,
            container: "container",
            task_menu: "contextmenu",
        };
        this.stage = new Konva.Stage({
            container: options.container,
            width: options.width,
            height: options.height,
            //draggable: true
        });
        this.layer = new Konva.Layer();
        this.stage.add(this.layer);
        this.task_menu = $(options.task_menu);
        this.margin_top = 40;
        this.margin_left = 100;
        this.task_node_width = 100;
        this.task_node_height = 30;

        this.stage.on('click', (e) => {
            this.task_menu.hide();
        });

        this.stage.on('contextmenu', (e) => {
            e.evt.preventDefault(true);
        });
    }

    batch_create_from_json(job_json) {
        let start_task_id = 0;
        $.each(job_json, (task_id, task_block) => {
            if (task_block.prev_task_ids.length === 0) {
                start_task_id = task_id;
            }
            task_block.post_task_ids = [];
            $.each(job_json, (next_task_id, next_task_block) => {
                if (next_task_block.prev_task_ids.indexOf(parseInt(task_id)) >= 0)
                    task_block.post_task_ids.push(next_task_id);
            });

            let task = this.create_task(task_block, this.margin_left, this.margin_top);
            task.attrs.level = 1;
        });
        let max_level_position = new Map();
        max_level_position.set(1, [this.margin_left, this.margin_top]);

        // 已知入口法
        let known_entry = [];
        // 网状图形时，不同的路径汇总到同一个task，之后再分散，此时需要通过connected控制同一个关系只被绘制一次
        let conntected = [];
        let has_drew = false;
        let task = this.layer.findOne("#" + start_task_id), next_task;
        while (1 === 1) {
            if (task.attrs.post_task_ids.length === 0 || has_drew === true) {
                if (known_entry.length === 0) break;
                let [task_id, next_task_id] = known_entry.pop().split('-');
                task = this.layer.findOne("#" + task_id);
                next_task = this.layer.findOne("#" + next_task_id);
                has_drew = false;
            } else {
                task.attrs.post_task_ids.reverse().map(x => known_entry.push(task.id() + "-" + x));
                next_task = this.layer.findOne("#" + known_entry.pop().split('-')[1]);
            }

            if (next_task.attrs.level === 1) {
                // level等于1代表该task为根或者没有重新定义过位置
                let next_task_level = task.attrs.level + 1,
                    x, y;

                if (max_level_position.has(next_task_level)) {
                    [x, y] = max_level_position.get(next_task_level);
                    y += this.margin_top + this.task_node_height;
                } else {
                    [x, y] = max_level_position.get(next_task_level - 1);
                    x += this.margin_left + this.task_node_width;
                }
                next_task.x(x);
                next_task.y(y);
                next_task.attrs.level = next_task_level;
                max_level_position.set(next_task_level, [x, y]);
            }

            if (conntected.indexOf(task.id() + "-" + next_task.id()) < 0) {
                this.create_relation(task, next_task);
                conntected.push(task.id() + "-" + next_task.id());
            } else {
                has_drew = true;
            }

            task = next_task;
        }
        return this;
    }

    create_task(task, x, y) {
        let group = new Konva.Group({
            x: x,
            y: y,
            id: "" + task.task_id,
            name: "task",
            type: task.task_type,
            command: task.task_content,
            status: 1,
            prev_task_ids: task.prev_task_ids,
            post_task_ids: task.post_task_ids,
            //opacity: 0.1,
            width: this.task_node_width,
            height: this.task_node_height,
            draggable: true,
        });
        group.add(new Konva.Rect({
            id: "rect-" + task.task_id,
            width: this.task_node_width,
            height: this.task_node_height,
            stroke: 'blue',
            cornerRadius: 0.6,
            strokeWidth: 0.5,
            shadowColor: "green",
            shadowBlur: 4,
            shadowEnabled: false,
            shadowOffset: {x: 1, y:1}
        }));
        group.add(new Konva.Text({
            id: "text-" + task.task_id,
            text: task.task_name,
            fontSize: 20,
            fontFamily: 'Calibri',
            width: this.task_node_width,
            height: this.task_node_height,
            padding: 5,
            align: 'center'
        }));
        this.layer.add(group);
        group.on('dragmove', () => this._update_connector_points(group.id()));
        group.on('mouseenter', () => {
            this.stage.container().style.cursor = 'move';
            group.findOne("#rect-"+group.id()).shadowEnabled(true);
            this.stage.draw();
        });
        group.on('mouseleave', () => {
            this.stage.container().style.cursor = 'default';
            group.findOne("#rect-"+group.id()).shadowEnabled(false);
            this.stage.draw();
        });
        group.on('contextmenu', (e) => {
            this.task_menu.css({"left": e.evt.x, "top": e.evt.y}).show();
            this.task_menu.attr("data-task-id", group.id());
            e.evt.preventDefault(true);
        });
        return group;
    }

    create_relation(from, to) {
        let relation = new Konva.Arrow({
            stroke: 'green',
            id: from.id() + "-" + to.id(),
            name: "relation",
            fill: 'green',
            strokeWidth: 0.8,
            pointerLength: 8,
            pointerWidth: 4,
            tension: 5,
            from: "" + from.id(),
            to: "" + to.id(),
            status: 1
        });
        relation.dash([8, 8]);
        this.layer.add(relation);
        relation.points(JobFlowPainter._get_connector_points(from, to));

    }

    static _get_connector_points(from, to) {
        return [
            from.position().x + from.width(),
            from.position().y + from.height() / 2,
            to.position().x,
            to.position().y + to.height() / 2
        ];
    }

    _update_connector_points(task_id) {
        let task = this.layer.findOne("#" + task_id);
        for (let child of this.layer.children) {
            if (child.name() === "relation") {
                if (child.attrs['from'] === task.id()) {
                    let to_task = this.layer.findOne("#" + child.attrs['to']);
                    let line = this.layer.findOne("#" + child.id());
                    line.points(JobFlowPainter._get_connector_points(task, to_task));
                } else if (child.attrs['to'] === task.id()) {
                    let from_task = this.layer.findOne("#" + child.attrs['from']);
                    let line = this.layer.findOne("#" + child.id());
                    line.points(JobFlowPainter._get_connector_points(from_task, task));
                }
            }

        }
        this.show();
    }

    show() {
        this.layer.batchDraw();
    }
}
