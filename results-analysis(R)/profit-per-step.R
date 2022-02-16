
plot_profit_per_step = function(df,colors){
  
    p = ggplot(df,aes(x=step,y = total_profit,col=Strategy,shape=Strategy),size=1)+
      geom_line()+
      geom_smooth(aes(group=Strategy, color = factor(Strategy)))+
      labs(x='Time steps',y='Profit per time step')+
      geom_ribbon(aes(ymin=total_profit-error,ymax=total_profit+error,fill=Strategy),alpha=0.1)+
      scale_x_continuous(breaks = scales::pretty_breaks(n = 5)) +
      scale_y_continuous(breaks = scales::pretty_breaks(n = 10)) +
      
      theme(legend.position = "top",
        legend.title = element_text(size=24),
        legend.text = element_text(size=20),
        axis.title = element_text(size=24),
        axis.text = element_text(size=20,color="black"),
        
        panel.grid.major.y = element_line(colour = "gray50", linetype="dashed"),
        
        panel.border = element_rect(colour = "black", fill=NA),
        panel.background = element_blank(), 
        axis.line = element_line(colour = "black")
      )+
      scale_color_manual(values = colors)+
      scale_fill_manual(values = colors)+
      guides(color=guide_legend(nrow=3, byrow=TRUE))
     
      
      
    return (p)
    
  }
  



compute_CI_error = function(data){
  sd_data = aggregate(total_profit~step+Strategy,data,sd)
  error = qt(0.975, df=nrow(data)-1)*sd_data$total_profit/sqrt(nrow(sd_data))
  return(error)
}


aggregated_data = function(d, socr,exp,rec_s){
  avg_profit_data = aggregate(total_profit~step+Strategy,d,mean)
  # compute the margin error of the 95% CI
  error = compute_CI_error(d)
  avg_profit_data$Strategy = rec_s
  avg_profit_data$reliance = socr
  avg_profit_data$expectation = exp
  avg_profit_data$error = error
  return(avg_profit_data)
}



process_profit_per_step= function(d,socr,exp,colors){
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


