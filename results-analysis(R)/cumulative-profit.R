windowsFonts(A=windowsFont("Times New Roman"))

plot_cumulative_profit= function(df,colors){
  
  p = ggplot(df,aes(x=step,y = cumsum_profit,col=strategy,shape=strategy),size=1)+
    geom_line(size=1)+
    labs(x='Time steps',y='Cumulative profit')+
    ylim(0,1500000)+
    scale_x_continuous(breaks = scales::pretty_breaks(n = 5)) +
    scale_y_continuous(labels = scales::unit_format(unit = "K", scale = 1e-3, sep = "",big.mark = ","),limits = c(0,1600000),breaks=seq(0,1600000,by=200000)) +
    geom_ribbon(aes(ymin=cumsum_profit-error,ymax=cumsum_profit+error,fill=strategy),alpha=0.1)+
    
    theme(legend.position = "none",
          text=element_text(family="A"),
          legend.title = element_text(size=24),
          legend.text = element_text(size=20),
          axis.title = element_text(size=24),
          axis.text = element_text(size=20,color="black"),
          #axis.text.x = element_text(angle = 90),
          panel.grid.major.y = element_line(colour = "gray70", linetype="dashed"),
          
          panel.border = element_rect(colour = "black", fill=NA),
          panel.background = element_blank(), 
          
          axis.line = element_line(colour = "black"),
    )+
    scale_color_manual(values = colors)+
    scale_fill_manual(values = colors)+
    guides(color=guide_legend(nrow=3, byrow=TRUE))

    #scale_fill_manual(values = colors)+
    #scale_color_manual(values = colors)
  
  return (p)
  }
  

compute_CI_error = function(data){
  sd_data = aggregate(total_profit~step+strategy,data,sd)
  error = qt(0.975, df=nrow(data)-1)*sd_data$total_profit/sqrt(nrow(sd_data))
  return(error)
}


aggregated_data = function(d,socr,exp, rec_s){
  avg_profit_data = aggregate(total_profit~step+strategy,d,mean)
  avg_profit_data$cumsum_profit = cumsum(avg_profit_data$total_profit)
  # compute the margin error of the 95% CI
  error = compute_CI_error(d)
  avg_profit_data$error = error
  avg_profit_data$reliance = socr
  avg_profit_data$expectation = exp
  avg_profit_data$strategy = rec_s
  return(avg_profit_data)
}



process_cumulative_profit = function(d,socr,exp,colors){
  #aggregate all data seperately
  d1 = aggregated_data(data.frame(d[1]),socr,exp,"Consumer-centric")
  d2 = aggregated_data(data.frame(d[2]),socr,exp,"Balanced")
  d3 = aggregated_data(data.frame(d[3]),socr,exp,"Profit-centric")
  d4 = aggregated_data(data.frame(d[4]),socr,exp,"Consumer-biased")
  d5 = aggregated_data(data.frame(d[5]),socr,exp,"Popularity-based")
  df = do.call("rbind",list(d1,d2,d3,d4,d5))
  
  df = do.call("rbind",list(d1,d2,d3,d4,d5))
  #p = plot(df,colors)
  return(df)
  
  # save plot
  # png(filename= file.path(newdir,"time-totalprofitplot.png"))
  # print(plot(df))
  # dev.off()
  
}


