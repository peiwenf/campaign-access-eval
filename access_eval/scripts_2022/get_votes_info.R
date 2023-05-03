#Libraries
library(rvest)
library(stringr)
library(tidyverse)
library(RCurl)
library(plyr)
library(rlang)
library(writexl)
library(magrittr)
library(stringi)

#Functions
`%notin%` <- Negate(`%in%`)

#import dataframe
df <- read.table("/Users/fpw/Desktop/research/campaign-access-eval/access_eval/analysis/data_2022/Mayor_cleaned.csv", 
                 header=TRUE, sep=",")

votes_share <- list()
votes <- list()
total_votes <- list()
current_l = ""
for (i in 1:nrow(df)) {
  if(df[i,2] != current_l){
    current_l = df[i,2]
    print(current_l)
    city_tracker = gsub(",.*$","",current_l)
    url <- df$CandPage[i]
    city_tracker = "Anchorage"
    url <- "https://ballotpedia.org/Kameron_Perez-Verdia"
    webpage <- read_html(url) #Reads the URL
    
    #Retrieves the election type, year, and candidate names for all elections on the page
    states <- html_nodes(webpage,  'h3>span, .rcvrace_header, .electionsectionheading, .votebox-header-election-type, .votebox-results-cell--text ,
                         .votebox-results-cell--number, .results_text') 
    
    names <- html_text(states) #Changes the list to a vector
    
    #Find the right place
    start_index = if(TRUE %in% grepl("election", names)){
      min(grep("election", names))
    }else{stop("new indicator needed")}
    names <- {names[start_index:length(names)]}
    
    #Reads how many candidates there are for 2022
    rows <- if(is_empty(names)==TRUE){0
    }else{if(TRUE %in% grepl("2020|2018|2019|2016|District history|primary|Withdrawn", names)){ifelse(min(grep("2020|2018|2019|2016|District history|primary|Withdrawn", names))==1, 0, min(grep("2020|2018|2016|2019|District history|primary|Withdrawn", names))-1)
    }else{length(names)}} 
    
    #Extracts names based on rows (Also accounts for new districts in 2022)
    #*Replace "runoff" with "lection" for governor
    names <- if(rows %in% c(0,1)){0}else{names[1:rows]}
    scrape_tracker = if(TRUE %in% grepl("runoff", names)){
      max(grep("runoff", names))
    }else if(TRUE %in% grepl(city_tracker, names)){
      max(grep(city_tracker, names))
    }else{stop("new indicator needed")}
    names <- names[scrape_tracker:(min(grep("Total votes", names)))]
    
    votes_df <- data.frame(names) %>% mutate(names = ifelse(names=="NA", NA, 
                                                            str_remove_all(names, "\\(.*") %>% str_trim())) %>% 
      filter(!row_number() %in% c(1))
    votes_df[nrow(votes_df),1] <- votes_df[nrow(votes_df),1] %>% str_sub( 14, -1)
    
    pattern = 3
    tracker = 2
    if(length(votes_df)>5) {
      if(votes_df[5,] == 'Won'){
        pattern = 5
        tracker = 5}}
    for( j in seq(1, (nrow(votes_df)-1), pattern)){
      if((votes_df[j,] != "Other/Write-in votes") & ((nrow(votes_df)-1 - j) >= tracker)){
        print(j)
        i_votes_share = as.numeric(votes_df[j+1,])/100
        i_votes = votes_df[j+2,]
        i_total_votes = votes_df[nrow(votes_df),]
        print(i_votes_share)
        print(i_votes)
        print(i_total_votes)
        votes_share = append(votes_share, i_votes_share)
        votes = append(votes, i_votes)
        total_votes = append(total_votes, i_total_votes)}
    }
  }
}
df$VotesForRace <- total_votes
df$VotesForCandidate <- votes
df$VoteShare <- votes_share

df_f<- apply(df,2,as.character)
write.csv(df_f, "/Users/fpw/Desktop/research/campaign-access-eval/access_eval/analysis/data_2022/Local_Elections_cleaned.csv", row.names=FALSE)


# for City/Municipal

#import dataframe
df <- read.table("/Users/fpw/Desktop/research/campaign-access-eval/access_eval/analysis/data_2022/Municipal_Elections_cleaned1.csv", 
                 header=TRUE, sep=",")
df <- read.table("/Users/fpw/Desktop/research/campaign-access-eval/access_eval/analysis/data_2022/City_Elections_cleaned1.csv", 
                 header=TRUE, sep=",")
votes_share <- list()
votes <- list()
total_votes <- list()
cand_pages <- list()
locations <- list()
races <- list()
areas <- list()
name_list <- list()
results <- list()
name_tracker = ''
for (i in 1:nrow(df)) {
  cat("large:", i)
  city_tracker = gsub(".*, ","",df[i,2]) 
  city_tracker = paste(" ", city_tracker, " ")
  url <- df$candidate_page[i]
  webpage <- read_html(url) #Reads the URL
  
  states <- html_nodes(webpage,  'h4, h3>span, div>div>p>label, .rcvrace_header, .electionsectionheading, .votebox-header-election-type, .votebox-results-cell--text ,
                       .votebox-results-cell--number') 
  
  #Reads how many candidates there are for 2022
  if(df[i,1]=="Andy Eads"){
    states <- states[min(grep("General election", states)):length(states)]
  }else{
    states <- if(TRUE %in% grepl("id=\"2022\"", states)){
      states[max(grep("id=\"2022\"", states)):length(states)]}else{next}
    if(min(grep("2020|2021|2019|2018|2016|District history|
                    primary|Withdrawn|survey responses", states))%in% c(1,2)){
      states <- states[max(grep("id=\"2022", states)):length(states)]
    }}
  rows <- if(is_empty(states)==TRUE){0
  }else{if(TRUE %in% grepl("2020|2021|2019|2018|2016|District history|
                           primary|Withdrawn|survey responses", states)){
    min(grep("2020|2021|2018|2019|2016|District history|primary|Withdrawn|survey responses", states))-1
  }else{length(states)}} 
  
  #Extracts names based on rows (Also accounts for new districts in 2022)
  states <- if(rows %in% c(0,1)){0}else{states[1:rows]}
  #for the races with rounds
  if(TRUE %in% grepl("Select round:", states)){
    scrape_tracker = min(grep("Select round:", states))
    round_tracker = html_text(states[scrape_tracker+1]) %>% str_trim()
    end_tracker = grep(round_tracker, states)[2]
    total_v_tracker = states[min(grep("Total votes", states))]
    states <- states[scrape_tracker:(end_tracker-1)]
    states[length(states)+1] = total_v_tracker
  }else{
    #for the races that contains runoff info
    end_tracker <- if(TRUE %in% grepl("runoff", states)){
      min(grep("General election", states))
    }else if(TRUE %in% grepl("Total votes", states)){
      min(grep("Total votes", states))
    }else{
      length(states)
    }
    states <- states[1:end_tracker]
    scrape_tracker = if(TRUE %in% grepl("runoff", states)){
      max(grep("runoff", states))
    }else{
      if(TRUE %in% grepl(city_tracker, states) & TRUE %in% grepl("lection", states)){
        max(max(grep("lection", states)), max(grep(city_tracker, states)))} else if(TRUE %in% grepl("lection", states)){
          max(grep("lection", states))
        }else if(TRUE %in% grepl(city_tracker, states)){
          max(grep(city_tracker, states))
        }else{1}}
    end_tracker <- if(TRUE %in% grepl("runoff", states)){
      min(grep("General election", states))
    }else if(TRUE %in% grepl("Total votes", states)){
      min(grep("Total votes", states))
    }else{
      length(states)
    }
    states <- states[scrape_tracker:length(states)]
  }
  
  links <- na.omit(data.frame(as.character(states)%>% str_extract("https.+?(?=(\"))")))
  names <- html_text(states) #Changes the list to a vector
  votes_df <- data.frame(names) %>% mutate(names = ifelse(names=="NA", NA, 
                                                          str_remove_all(names, "\\(.*") %>% str_trim()))
  if((FALSE %in% grepl("\\(", names[1])) | (TRUE %in% grepl("lection", names[1]))|(TRUE %in% grepl("Select round:", names[1]))){
    votes_df <- votes_df %>% filter(!row_number() %in% c(1))}
  if(lengths(votes_df[1]) < 2){next}
  if((str_length(votes_df[nrow(votes_df),])>3) & 
     (FALSE %in% grepl(",", votes_df[nrow(votes_df),])& 
      (FALSE %in% grepl("Total votes", votes_df[nrow(votes_df),])))){
    votes_df <- votes_df %>% filter(!row_number() %in% c(nrow(votes_df)))}
  if(votes_df$names[1] != name_tracker){
    name_tracker = votes_df$names[1]
  }else{
    next
  }
  if(lengths(votes_df[1]) > 2){
    if(sum(str_detect(votes_df$names, 'Total votes'))>0){
      pattern = 3
      tracker = 2
      if(lengths(votes_df[1]) > 5){
        if(votes_df[5,] == 'Won'){
          pattern = 5
          tracker = 4} 
      }
      # handle the races that has more than 1 winner
      if((TRUE %in% grepl("seats", names[1])) & (as.numeric(votes_df[2,])/100 < 0.3)){
        seats_tracker = sub(".*?(\\d+(,\\d+)?)\\s+seats.*", "\\1", names[1])
        cat("check:", i)
        #stop("check!")
      }else if(as.numeric(votes_df[2,])/100 < 0.3){
        cat("check check", i)
      }else{
        seats_tracker = 1
      }
      for( j in seq(1, (nrow(votes_df)-1), pattern)){
        if((votes_df[j,] != "Other/Write-in votes") & ((nrow(votes_df)-1 - j) >= tracker)){
          cat("small:", j)
          i_name = votes_df[j,]
          i_votes_share = as.numeric(votes_df[j+1,])/100
          i_votes = votes_df[j+2,]
          i_total_votes = votes_df[nrow(votes_df),] %>% str_sub( 14, -1)
          i_link = links[(j+tracker)/pattern,]
          i_location = df[i,2]
          i_race = df[i,5]
          i_area = df[i,6]
          if(j %in% seq(1, (nrow(votes_df)-1), pattern)[1:seats_tracker]){
            i_result = "Won"
          }else{i_result = "Lost"}
          name_list = append(name_list, i_name)
          votes_share = append(votes_share, i_votes_share)
          votes = append(votes, i_votes)
          total_votes = append(total_votes, i_total_votes)
          cand_pages = append(cand_pages, i_link)
          locations = append(locations, i_location)
          races = append(races, i_race)
          areas = append(areas, i_area)
          results = append(results, i_result)}
      }
    }else{
      print("in else")
      i_name = df[i,1]
      i_votes_share = as.numeric(votes_df[1,])/100
      i_votes = votes_df[2,]
      i_total_votes = votes_df[nrow(votes_df),]
      i_link = df[i,4]
      i_location = df[i,2]
      i_race = df[i,5]
      i_area = df[i,6]
      i_result = "Won"
      name_list = append(name_list, i_name)
      votes_share = append(votes_share, i_votes_share)
      votes = append(votes, i_votes)
      total_votes = append(total_votes, i_total_votes)
      cand_pages = append(cand_pages, i_link)
      locations = append(locations, i_location)
      races = append(races, i_race)
      areas = append(areas, i_area)
      results = append(results, i_result)
    }
  }else{
    print("no voting")
    for(j in 1:nrow(votes_df)){
      i_name = votes_df$names[j]
      i_votes_share = NA
      i_votes = NA
      i_total_votes = NA
      i_result = NA
      i_link = links[j,]
      i_location = df[i,2]
      i_race = df[i,5]
      i_area = df[i,6]
      name_list = append(name_list, i_name)
      votes_share = append(votes_share, i_votes_share)
      votes = append(votes, i_votes)
      total_votes = append(total_votes, i_total_votes)
      cand_pages = append(cand_pages, i_link)
      locations = append(locations, i_location)
      races = append(races, i_race)
      areas = append(areas, i_area)
      results = append(results, i_result)
    }
  }
}
new_df = data.frame(unlist(name_list), 
                    unlist(locations),
                    unlist(cand_pages), 
                    unlist(races),
                    unlist(areas), 
                    unlist(results),
                    unlist(total_votes),
                    unlist(votes), 
                    unlist(votes_share))
new_df <- new_df %>% distinct() # remove duplicates

# rename the columns
names(new_df) = c("names", "location", "candidate_page", "race", "area", "election_result", "number_of_votes_for_race", "number_of_votes_for_candidate", "vote_share")
MuNamesFin = new_df
MuNamesFin["candidate_page"][MuNamesFin["candidate_page"] == "https://ballotpedia.org/Kelly_Rowe"] <- "https://ballotpedia.org/Kelly_Rowe_(California)"
MuNamesFin["candidate_page"][MuNamesFin["candidate_page"] == "https://ballotpedia.org/Todd_Robinson"] <- "https://ballotpedia.org/Todd_Robinson_(Texas)"

Handles <- data.frame()
for(i in 1:nrow(MuNamesFin)){
  #Goes to candidate links (if working)
  if(is.na(MuNamesFin[i,1])==FALSE & url.exists(MuNamesFin[i, 3])==TRUE){
    InfoPage <- read_html(MuNamesFin[i, 3])
    links <- InfoPage %>% html_nodes("a") %$% data.frame(hrefs=as(., "character")) #Reads webpage
    
    #Identifies Campaign Website
    CampWeb <- links[grep("Campaign website|Official website|Personal website", links$hrefs), 1] %>% str_extract("http.+?(?=(\" t))")
    CampWeb <- ifelse(is_empty(CampWeb)==TRUE, NA, CampWeb)
    
    #Identifies Campaign Twitter Handle
    CampHand <- links[grep("www.twitter.*Camp", links$hrefs), 1] %>% str_remove(".*com\\/") %>% str_remove("(\").*")
    CampHand <- ifelse(is_empty(CampHand)==TRUE, NA, CampHand)
    
    #Identifies Official Twitter Handle
    OffHand <- links[grep("www.twitter.*Off", links$hrefs), 1] %>% str_remove(".*com\\/") %>% str_remove("(\").*")
    OffHand <- ifelse(is_empty(OffHand)==TRUE, NA, OffHand)
    
    #Identifies Personal Twitter Handle
    PerHand <- links[grep("www.twitter.*Pers", links$hrefs), 1] %>% str_remove(".*com\\/") %>% str_remove("(\").*")
    PerHand <- ifelse(is_empty(PerHand)==TRUE, NA, PerHand)
    
    #Identifies Party
    partyLink <- InfoPage %>% html_nodes(".widget-row.value-only") %$% data.frame(hrefs=as(., "character"))
    Party <- ifelse(is_empty(grep("black", partyLink$hrefs))==FALSE,
                    partyLink[max(grep("black", partyLink$hrefs)),1] %>% str_sub(49,-15),
                    ifelse(is_empty(grep("Party|Independent|Unaffiliated|Nonpartisan", partyLink$hrefs)),
                           links[max(grep("Category.*Party|Independent|Unaffiliated|Nonpartisan", links$hrefs)), 1] %>% str_remove(".*Category:") %>% str_remove("(\").*"),
                           partyLink[max(grep("Party|Independent|Unaffiliated|Nonpartisan", partyLink$hrefs)),1]%>% 
                             str_extract("only.*(\")") %>% str_sub(6,-2)))
    
    Party <- ifelse(is_empty(Party)==TRUE, NA, Party)
    
    #Creates the dataframe
    df <- data.frame(Names=MuNamesFin[i,1], CampWeb, CampHand, OffHand, PerHand, Party)
  }else {df <- data.frame(Names= MuNamesFin[i,1], CampWeb = NA, CampHand = NA, OffHand = NA, PerHand = NA, Party=NA)} #Accounts for non-working links
  Handles <- rbind(Handles, df)
}

MuNamesFin <- cbind(MuNamesFin, Handles %>% select(-Names))

MuNamesFin<- apply(MuNamesFin,2,as.character)
write.csv(MuNamesFin, "/Users/fpw/Desktop/research/campaign-access-eval/access_eval/analysis/data_2022/Municipal_Elections_cleaned.csv", row.names=FALSE)