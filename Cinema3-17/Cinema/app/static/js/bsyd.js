// 基于准备好的dom，初始化echarts实例
var myChart1 = echarts.init(document.getElementById('chart_box'));


function mychart1(time, table_rows) {
    var films = table_rows.map(function(item) {
        return item.FilmName
    });
    var values = table_rows.map(function(item) {
        return item.Sum
    });
    //配置及数据
    optionyear = {
        title: {
            text: "Weekly takings",
            padding: [10, 100, 10, 500], // 标题位置
            subtext: "",
            textAlign: "center",
        },
        tooltip: {
            formatter: '{c}',
            trigger: 'axis',    //提示触发类型      'item':数据项图形触发，主要在散点图，饼图等无类目轴的图表中使用。
            //'axis':坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
            //'none':什么都不触发。
            show: true,     //是否显示提示框组件 默认为true
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            }
        },
        legend: {
            data: ['']
        },
        xAxis: [
            {
                type: 'category',
                data: films,
                axisPointer: {
                    type: 'shadow'
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: '',
                min: 0,
                max: 100.00,
                splitNumber: 10,
                axisLabel: {
                    formatter: '{value}',
                }
            },
        ],
        series: [
            {
                name: '',
                type: 'bar',         //bar表示柱状图
                barWidth: 20,
                data: values,//数据
                itemStyle: {    //更多柱状图样式搜索API：series-bar.itemStyle
                    normal: {
                        color: '#1E90FF',//改变柱状的颜色
                        label: {
                            show: true, //开启显示
                            position: 'top', //在上方显示
                            formatter: '{c}',   //百分比显示
                            textStyle: { //数值样式
                                color: 'black',    //柱上数据颜色
                                fontSize: 16
                            }
                        }
                    }
                },
            },
        ]
    };
    // 使用刚指定的配置项和数据显示图表。
    myChart1.setOption(optionyear);
}