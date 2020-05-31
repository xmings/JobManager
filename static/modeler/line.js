export class Line {
    constructor(group) {
        this.group = group;
        this.source = [];
        this.target = [];
        this.relationId = 1;
        this.focusDistance = 20;
        this.srcLines = [];
        this.tgtLines = [];
    }

    fetchFocusPos() {
        let srcYList = this.source.map(function (item) { return item[1] }),
            tgtYList = this.target.map(function (item) { return item[1] }),
            srcMidY = (Math.max(...srcYList) - Math.min(...srcYList)) / 2 + Math.min(...srcYList),
            tgtMidY = (Math.max(...tgtYList) - Math.min(...tgtYList)) / 2 + Math.min(...tgtYList),
            //理论上this.source和this.target各自中的坐标list中x坐标相同，所以取第一个即可
            srcMidX = this.source[0][0],
            tgtMidX = this.target[0][0];

        let rate = Math.abs((srcMidY - tgtMidY) / (srcMidX - tgtMidX));
        this.srcFocusX = srcMidX < tgtMidX ? srcMidX + this.focusDistance : srcMidX - this.focusDistance;
        this.srcFocusY = srcMidY < tgtMidY ? srcMidY + rate * this.focusDistance : srcMidY - rate * this.focusDistance;
        this.tgtFocusX = srcMidX < tgtMidX ? tgtMidX - this.focusDistance : tgtMidX + this.focusDistance;
        this.tgtFocusY = srcMidY < tgtMidY ? tgtMidY - rate * this.focusDistance : tgtMidY + rate * this.focusDistance;

        //两个FocusY坐标不能超过两个MidY坐标的范围
        if (this.srcFocusY < Math.min(srcMidY, tgtMidY)
            || this.srcFocusY > Math.max(srcMidY, tgtMidY)) {
            this.srcFocusX = srcMidX;
            this.srcFocusY = srcMidY;
            this.tgtFocusX = tgtMidX;
            this.tgtFocusY = tgtMidY;
        }
    }

    start() {
        this.fetchFocusPos();

        for (let pos of this.source) {
            let line = new Konva.Line({
                points: [pos[0], pos[1], this.srcFocusX, this.srcFocusY],
                stroke: 'black',
            });
            this.srcLines.push(line);
            this.group.add(line);
        }

        for (let pos of this.target) {
            let line = new Konva.Line({
                points: [pos[0], pos[1], this.tgtFocusX, this.tgtFocusY],
                stroke: 'black',
            });
            this.tgtLines.push(line);
            this.group.add(line);
        }

        this.arrow = new Konva.Arrow({
            points: [this.srcFocusX, this.srcFocusY, this.tgtFocusX, this.tgtFocusY],
            pointerLength: 10,
            pointerWidth: 10,
            fill: 'black',
            stroke: 'black'
        });
        this.group.add(this.arrow);

        let srcText, tgtText;
        if (this.relationId === 2){
            srcText = '1';
            tgtText = 'N';
        } else if (this.relationId === 3){
            srcText = 'N';
            tgtText = '1';
        } else if (this.relationId === 4){
            srcText = 'N';
            tgtText = 'N';
        } else {
            srcText = '1';
            tgtText = '1';
        }  

        this.srcLabel = new Konva.Text({
            x: this.srcFocusX,
            y: this.srcFocusY,
            text: srcText,
            fontSize: 14,
            stroke: "#FFC107"
        });

        this.group.add(this.srcLabel);

        this.tgtLabel = new Konva.Text({
            x: this.tgtFocusX,
            y: this.tgtFocusY,
            text: tgtText,
            fontSize: 14,
            stroke: "#FFC107"
        });

        this.group.add(this.tgtLabel);
    }

    move() {
        this.fetchFocusPos();
        let i = 0;
        for (let sl of this.srcLines) {
            let [x, y] = this.source[i];
            sl.setAttr("points", [x, y, this.srcFocusX, this.srcFocusY]);
            i++;
        }
        i = 0;
        for (let tl of this.tgtLines) {
            let [x, y] = this.target[i];
            tl.setAttr("points", [x, y, this.tgtFocusX, this.tgtFocusY]);
            i++;
        }

        this.arrow.setAttr("points", [this.srcFocusX, this.srcFocusY, this.tgtFocusX, this.tgtFocusY]);

        this.srcLabel.x(this.srcFocusX);
        this.srcLabel.y(this.srcFocusY);

        this.tgtLabel.x(this.tgtFocusX);
        this.tgtLabel.y(this.tgtFocusY);
    }
}
