windowsFonts(A=windowsFont("Times New Roman"))

plot_consumption = function(df,colors){
  p = ggplot(df,aes(step,consumption_probability,col=strategy),size=1)+
    geom_line(size=1)+
    geom_ribbon(aes(ymin=consumption_probability-error,ymax=consumption_probability+error,fill=strategy),alpha=0.1)+
    scale_x_continuous(breaks = scales::pretty_breaks(n = 5)) +
    scale_y_continuous(limits = c(0.2,1), breaks = seq(0.2,1, by=0.1)) +
    
    labs(x='Time steps',y='Consumption probability')+
    
    theme(legend.position = "none",
          text=element_text(family="A"),
          legend.title = element_text(size=24),
          legend.text = element_text(size=20),
          axis.title = element_text(size=24),
          axis.text = element_text(size=20,color="black"),
          #axis.text.x = element_text(angle = 90),
          panel.grid.major.x = element_blank(),
          panel.grid.minor.x = element_blank(),
          panel.grid.major.y = element_line(colour = "gray50", linetype="dashed"),
          
          panel.background = element_blank(), 
          panel.border = element_rect(colour = "black", fill=NA),
          
          axis.line = element_line(colour = "black"),
          
          #legend.box="vertical",
          #legend.margin=margin()
    )+
    scale_color_manual(values = colors)+
    scale_fill_manual(values = colors)+
    guides(color=guide_legend(nrow=3, byrow=TRUE))
    
  return(p)
}



          
aggregated_data = function(d,socr,rec_str){
  avg_consumption_probability_data = aggregate(consumption_probability~step+strategy,d,mean)
  # compute the margin error of the 95% CI
  error = compute_CI_error(d)
  avg_consumption_probability_data$error = error
  avg_consumption_probability_data$reliance = socr
  avg_consumption_probability_data$strategy = rec_str
  return(avg_consumption_probability_data)
}

     

compute_CI_error = function(d,t){
  sd_data = aggregate(consumption_probability~step+strategy,d,sd)
  error = qt(0.975, df=nrow( sd_data)-1)*sd_data$consumption_probability/sqrt(nrow(sd_data))
  return(error)
}



prepare_consumption = function(d,socr,colors){
  #aggregate all data seperately
  d1 = aggregated_data(data.frame(d[1]),socr,"Consumer-centric")
  d2 = aggregated_data(data.frame(d[2]),socr,"Balanced")
  d3 = aggregated_data(data.frame(d[3]),socr,"Profit-centric")
  d4 = aggregated_data(data.frame(d[4]),socr,"Consumer-biased")
  d5 = aggregated_data(data.frame(d[5]),socr,"Popularity-based")
  df = do.call("rbind",list(d1,d2,d3,d4,d5))
  
 # p = plot(df,colors)
  
  return(df)
}
