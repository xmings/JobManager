export class Table {
    constructor(group){
        this.group = group;
        this.headerWidth = 0;
        this.headerHeight = 40;
        this.cellHeight = 20;
        this.cellWidth = [140, 120, 200];
        this.cellAlign = ["left", "left", "left"];
        this.rowCount = 0;
        this.columnNames = [];
    }

    setHeader(tableName) {
        this.tableName = tableName;
        this.headerWidth = this.cellWidth.reduce((x,y)=>x+y);
        this.group.add(new Konva.Rect({
            x: 0,
            y: 0,
            width: this.headerWidth,
            height: this.headerHeight,
            fill: "white",
            stroke: 'black',
            strokeWidth: 1
        }));
    
        this.group.add(new Konva.Text({
            x: 0,
            y: 0,
            name: "header",
            text: this.tableName,
            fontSize: 20,
            fontFamily: 'Calibri',
            width: this.headerWidth,
            height: this.headerHeight,
            padding: 10,
            align: 'center'
        }))
    }

    addRow(columnName, dataType, notNull) {
        let cellText = [columnName, dataType, notNull];
        let startX = 0, startY = this.headerHeight + this.cellHeight*this.rowCount;
        this.columnNames.push(columnName);
    
        for (let i=0;i<this.cellWidth.length; i++){
            this.group.add(new Konva.Rect({
                x: startX,
                y: startY,
                width: this.cellWidth[i],
                height: this.cellHeight,
                fill: "white",
                stroke: 'black',
                strokeWidth: 1
            }));
        
            this.group.add(new Konva.Text({
                x: startX,
                y: startY,
                width: this.cellWidth[i],
                height: this.cellHeight,
                text: cellText[i],
                fontSize: 14,
                fontFamily: 'Calibri',
                padding: 3,
                align: this.cellAlign[i]
            }));
    
            startX += this.cellWidth[i];
        }
        this.rowCount += 1;
    }

    updateCell(columnName, dataType, notNull) {
    
    }
    
}