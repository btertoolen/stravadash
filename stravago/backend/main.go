package main

import (
	"encoding/json"
	"io"
	"os"
	"stravago/stravago"
)

type Config struct {
	ClientID     string `json:"client_id"`
	ClientSecret string `json:"client_secret"`
	RefreshToken string `json:"refresh_token"`
}

func main() {
	// Read json from ../../user/bram.json
	f, err := os.Open("../../user/bram.json")
	if err != nil {
		panic(err)
	}
	// Read the contents of the file
	data, err := io.ReadAll(f)
	if err != nil {
		panic(err)
	}

	// parse json into config struct
	var config Config
	err = json.Unmarshal(data, &config)
	if err != nil {
		panic(err)
	}

	new_refresh_token := stravago.Authenticate(config.ClientID, config.ClientSecret, config.RefreshToken)
	config.RefreshToken = new_refresh_token
	configJSON, err := json.Marshal(config)
	if err != nil {
		panic(err)
	}

	f.Write(configJSON)
	f.Close()

	volume_result := stravago.GetWeeklyVolumes()
	f, err = os.Create("../../data/weekly_volumes.json")
	if err != nil {
		panic(err)
	}
	if volume_result == "" {
		panic("volume_result is empty")
	}
	f.Write([]byte(volume_result))

	pace_hr_result := stravago.GetPaceAndHeartRate()
	f, err = os.Create("../../data/pace_hr.json")
	if err != nil {
		panic(err)
	}
	if len(pace_hr_result) < 50 {
		panic("received empty pace_hr data")
	}
	f.Write([]byte(pace_hr_result))

	totals := stravago.GetAthleteRunningStats()
	f, err = os.Create("../../data/running_total.json")
	if err != nil {
		panic(err)
	}
	if len(totals) < 50 {
		panic("received empty running totals")
	}
	f.Write(totals)

}
