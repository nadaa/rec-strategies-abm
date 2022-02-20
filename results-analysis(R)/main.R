
#------------------- Readme--------------------------------------------------------------------------------------
# To generate the figures, uncomment the plots as desired.
# Highlight the code and press on Run
# All required packages will be installed automatically
# A new popup window will as you to select the data directory
# Highlight the code to run
# When completing the execution, a new directory named as "Figures" is generated in the same directory of the data.

#----------------------------------------------------------------------------------------------------------------


# List of the required packages
.packages = c("ggplot2", "cowplot", "scales")

# Install CRAN packages (if not already installed)
.inst = .packages %in% installed.packages()
if(length(.packages[!.inst]) > 0) install.packages(.packages[!.inst])

# Load packages into session 
lapply(.packages, require, character.only=TRUE)



# set the colors
colors = c("Consumer-centric"="cornflowerblue","Balanced"="red","Consumer-biased"="mediumorchid1","Profit-centric"= "black","Popularity-based"="mediumseagreen")


datapath = choose.dir(getwd(), "Choose the results folder")
setwd(datapath)


read_agents_data = function(str,nsteps = 1000){
  # read all the data
  agents_data1= subset(read.csv(paste(str,"agents-data-scenario1.csv",sep="")),step<=nsteps)
  agents_data2= subset(read.csv(paste(str,"agents-data-scenario2.csv",sep="")),step<=nsteps)
  agents_data3= subset(read.csv(paste(str,"agents-data-scenario3.csv",sep="")),step<=nsteps)
  agents_data4= subset(read.csv(paste(str,"agents-data-scenario4.csv",sep="")),step<=nsteps)
  agents_data5= subset(read.csv(paste(str,"agents-data-scenario5.csv",sep="")),step<=nsteps)
  
  return (list(agents_data1, agents_data2, agents_data3, agents_data4,agents_data5))
}


read_model_data = function(str){
  model_data1= subset(read.csv(paste(str,"model-data-scenario1.csv",sep="")),step>0)
  model_data2= subset(read.csv(paste(str,"model-data-scenario2.csv",sep="")),step>0)
  model_data3= subset(read.csv(paste(str,"model-data-scenario3.csv",sep="")),step>0)
  model_data4= subset(read.csv(paste(str,"model-data-scenario4.csv",sep="")),step>0)
  model_data5= subset(read.csv(paste(str,"model-data-scenario5.csv",sep="")),step>0)
  
  return (list(model_data1, model_data2,model_data3,model_data4,model_data5))
  
}


# get the path of the main script
scriptspath = dirname(rstudioapi::getSourceEditorContext()$path)


newdir = "Figures"
dir.create(newdir,showWarnings = FALSE)



plot_figures= function(newdir,colors) {
  # trust
  # source(paste(scriptspath,"/trust.R",sep=''))
  # agents_data = read_agents_data("")
  # trust_df= process_trust(agents_data,0.75,colors)
  # trust = plot_trust(trust_df,colors)
  # 
  #consumption plot
  source(paste(scriptspath,"/consumption.R",sep=''))
  agents_data = read_agents_data("")
  consumption_df= prepare_consumption(agents_data,0.75,colors)
  consumption = plot_consumption(consumption_df,colors)


  # profit per step 
  source(paste(scriptspath,"/profit-per-step.R",sep=''))
  model_data= read_model_data("")
  profit_per_step_df= process_profit_per_step(model_data,0.0,0.75,colors)
  profit_per_step=plot_profit_per_step( profit_per_step_df,colors)
  
  # time-cumulative-profit 
  source(paste(scriptspath,"/cumulative-profit.R",sep=''))
  cumulative_profit_df = process_cumulative_profit(model_data,0.0,0.75,colors)
  cumulative_profit = plot_cumulative_profit(cumulative_profit_df,colors)
  
  # Save each plots seperately
  #---------------------------------
  
  # png(filename= file.path(newdir,"trust.png"),width=530)
  # print(trust)
  # dev.off()
  # 
  png(filename= file.path(newdir,"consumption.png"),width=530)
  print(consumption)
  dev.off()

  png(filename= file.path(newdir,"profit-per-step.png"),width=530)
  print(profit_per_step)
  dev.off()

  png(filename= file.path(newdir,"cumulative-profit.png"),width=530)
  print(cumulative_profit)
  dev.off()
  
  
}






# Figures of trust, profit per time step, and cumulative profit 
#-------------------------------------------------------------
plot_figures(newdir,colors)
