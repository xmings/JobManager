import {Line} from './line.js';
import {Table} from './table.js';

class Relation {
    constructor(srcTable, tgtTable) {
        this.srcTable = srcTable;
        this.tgtTable = tgtTable;
        this.srcColumns = [];
        this.tgtColumns = [];
        this.line = null;
    }
}

export class Designer {
    constructor(options) {
        options = options || {
            container: "container",
            contextmenu: "contextmenu"
        };
        this.zoomLevel = 1;
        this.minZoomLevel = 0.5;
        this.maxZoomLevel = 3;
        this.stage = new Konva.Stage({
            container: options.container,
            width: window.innerWidth * this.maxZoomLevel,
            height: window.innerHeight * this.maxZoomLevel,
            draggable: true
        });
        this.contextmenu = $("#" + options.contextmenu);
        this.layer = new Konva.Layer();
        this.selectedTableName = null;
        this.gridInterval = 32;
        this.initGrid();
        this.tables = [];
        this.relations = [];
        this.stage.on('contextmenu', (e) => {
            if (!e.hasOwnProperty("end")) {
                this.contextmenu.find(".item").each((index, ele) => {
                    if (!$(ele).hasClass("global-level")) {
                        $(ele).hide();
                    }
                });
                this.contextmenu.css({"left": e.evt.x, "top": e.evt.y}).show();
                e.evt.preventDefault(true);
            }
        });

        this.stage.on('dragmove', (e) => {
            if (this.stage.x() > 0) {
                this.stage.x(0);
            }

            if (this.stage.y() > 0) {
                this.stage.y(0);
            }

            if (this.stage.x() + this.stage.width() * this.zoomLevel < this.stage.container().offsetWidth) {
                this.stage.x(this.stage.container().offsetWidth - this.stage.width() * this.zoomLevel);
            }

            if (this.stage.y() + this.stage.height() * this.zoomLevel < window.innerHeight) {
                this.stage.y(window.innerHeight - this.stage.height() * this.zoomLevel);
            }

        });

        this.stage.on('wheel', (e) => {
            let draw = false;
            if (this.zoomLevel > this.minZoomLevel && (e.evt.wheelDelta === -120 || e.evt.detail === -3)) {
                this.zoomLevel = this.zoomLevel / 1.2;
                draw = true;
            } else if (this.zoomLevel < this.maxZoomLevel && e.evt.wheelDelta === 120 || e.evt.detail === 3) {
                this.zoomLevel = this.zoomLevel * 1.2;
                draw = true;
            }

            if (draw === true) {
                this.layer.scale({
                    x: this.zoomLevel,
                    y: this.zoomLevel
                });
                this.layer.draw();
            }
        });
    }

    initGrid() {
        for (let i = 0; i < this.stage.width() / this.gridInterval; i++) {
            let line = new Konva.Line({
                points: [i * this.gridInterval, 0, i * this.gridInterval, this.stage.height()],
                stroke: 'gray',
                strokeWidth: 0.1,
                lineJoin: 'round',
                dash: [10, 8]
            });
            this.layer.add(line)
        }

        for (let i = 0; i < this.stage.height() / this.gridInterval; i++) {
            let line = new Konva.Line({
                points: [0, i * this.gridInterval, this.stage.width(), i * this.gridInterval],
                stroke: 'gray',
                strokeWidth: 0.1,
                dash: [10, 8]
            });
            this.layer.add(line)
        }

        this.stage.on("click", () => {
            this.contextmenu.hide();
        });

        this.contextmenu.find(".item").click(() => {
            this.contextmenu.hide();
        })
    }

    createTable(tableName, posX, posY) {
        let tableGroup = new Konva.Group({
            x: posX || 120,
            y: posY || 40,
            //rotation: 20,
            draggable: true,
        });
        let table = new Table(tableGroup);
        table.setHeader(tableName);
        this.tables.push(table);
        this.layer.add(tableGroup);

        tableGroup.on('dragmove', (e) => {
            this.contextmenu.hide();
            this.changeRelationPos(tableName, e);
        });

        tableGroup.on('mouseenter', () => {
            this.stage.container().style.cursor = 'move';
        });

        tableGroup.on('mouseleave', () => {
            this.stage.container().style.cursor = 'default';
        });

        tableGroup.on('contextmenu', (e) => {
            this.contextmenu.find(".item.table-level").each((index, ele) => {
                $(ele).css("display", "block");
            });
            this.contextmenu.css({"left": e.evt.x, "top": e.evt.y}).show();
            this.selectedTableName = tableName;
            e.end = true;
            e.evt.preventDefault(true);
        });

        return table;
    }

    fetchTableByName(tableName) {
        for (let t of this.tables) {
            if (t.tableName === tableName) {
                return t;
            }
        }
    }

    static fetchConnectPoint(srcTable, srcCols, tgtTable, tgtCols) {
        let srcColsPos = [], tgtColsPos = [];
        let srcX = srcTable.group.x() < tgtTable.group.x() ? srcTable.group.x() + srcTable.headerWidth : srcTable.group.x();
        let tgtX = srcTable.group.x() < tgtTable.group.x() ? tgtTable.group.x() : tgtTable.group.x() + tgtTable.headerWidth;

        for (let col of srcCols) {
            let srcY = srcTable.columnNames.indexOf(col) * srcTable.cellHeight + srcTable.cellHeight / 2 + srcTable.headerHeight + srcTable.group.y();
            srcColsPos.push([srcX, srcY]);
        }

        for (let col of tgtCols) {
            let tgtY = tgtTable.columnNames.indexOf(col) * tgtTable.cellHeight + tgtTable.cellHeight / 2 + tgtTable.headerHeight + tgtTable.group.y();
            tgtColsPos.push([tgtX, tgtY]);
        }
        return [srcColsPos, tgtColsPos];
    }

    drawRelation(srcTabName, srcColList, tgtTabName, tgtColList, relationId) {
        let srcTable = this.fetchTableByName(srcTabName),
            tgtTable = this.fetchTableByName(tgtTabName);

        this.relations = this.relations.filter(function (r) {
            if (r.srcTable === srcTable && r.tgtTable === tgtTable) {
                r.line.group.destroy(true);
                return false;
            }
            return true;
        });

        let relation = new Relation(srcTable, tgtTable);
        relation.srcColumns = srcColList;
        relation.tgtColumns = tgtColList;
        let lineGroup = new Konva.Group({
            draggable: false
        });
        this.layer.add(lineGroup);

        relation.line = new Line(lineGroup);
        relation.line.relationId = relationId || 1;
        [relation.line.source, relation.line.target] = Designer.fetchConnectPoint(srcTable, srcColList, tgtTable, tgtColList);
        relation.line.start();
        this.relations.push(relation);
        this.layer.draw();
    }


    changeRelationPos(tableName, e) {
        for (let rel of this.relations) {
            if (rel.srcTable.tableName === tableName || rel.tgtTable.tableName === tableName) {
                [rel.line.source, rel.line.target] = Designer.fetchConnectPoint(rel.srcTable, rel.srcColumns, rel.tgtTable, rel.tgtColumns);
                rel.line.move();
            }
        }
    }

    fetchAllTablesPos() {
        let tablesPos = {};
        for (let t of this.tables) {
            tablesPos[t.tableName] = t.group.x() + "," + t.group.y();
        }
        return tablesPos;
    }

    fetchTableRelation(srcTabName, tgtTabName) {
        for (let r of this.relations) {
            if (r.srcTable.tableName === srcTabName) {
                if ((typeof tgtTabName !== "undefined"
                    && r.tgtTable.tableName === tgtTabName)
                    || typeof tgtTabName === "undefined") {
                    return {
                        src: r.srcColumns,
                        tgtTable: r.tgtTable.tableName,
                        tgt: r.tgtColumns
                    }
                }
            }
        }
    }

    dropTableByTableName(tableName) {
        let dependence_tables = [];
        if (tableName !== null) {
            let table = this.fetchTableByName(tableName);
            this.relations = this.relations.filter(function (r) {
                if (r.srcTable === table || r.tgtTable === table) {
                    dependence_tables.push(r.srcTable === table ? r.tgtTable.tableName : r.srcTable.tableName);
                    r.line.group.destroy(true);
                    return false;
                }
                return true;
            });

            table.group.destroy(true);
            this.tables.splice(this.tables.indexOf(table), 1);
            this.layer.draw();
        }
        return dependence_tables;
    }

    showTableByKeyword(keyword, type) {
        let match_tables = [];
        this.layer.find(".header").setAttr("fill", "black");

        if (type === "schema") {
            for (let t of this.tables) {
                let shema = t.tableName.split(".")[0];
                if (shema.indexOf(keyword) >= 0) {
                    match_tables.push(t);
                }
            }
        } else if (type === "table") {
            for (let t of this.tables) {
                let table = t.tableName.split(".")[1];
                if (table.indexOf(keyword) >= 0) {
                    match_tables.push(t);
                }
            }
        } else if (type === "column") {
            for (let t of this.tables) {
                if (t.columnNames.some((x) => {
                    return x.indexOf(keyword) >= 0;
                })) {
                    match_tables.push(t);
                }
            }
        } else if (type === "description") {
            for (let t of this.tables) {
                if (t.descriptions.some((x) => {
                    return x.indexOf(keyword) >= 0;
                })) {
                    match_tables.push(t);
                }
            }
        }

        for (let t of match_tables) {
            t.group.find(".header").setAttr("fill", "#F44336");
        }
        this.layer.draw();
    }


    flush() {
        this.stage.add(this.layer);
    }
}