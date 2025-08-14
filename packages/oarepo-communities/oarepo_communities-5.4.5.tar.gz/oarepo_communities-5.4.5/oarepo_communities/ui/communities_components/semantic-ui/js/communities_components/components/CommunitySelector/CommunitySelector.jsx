import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { useFormConfig, goBack } from "@js/oarepo_ui";
import { useFormikContext, getIn } from "formik";
import { Message, Icon, Modal, List, Button } from "semantic-ui-react";
import { Trans } from "react-i18next";
import { i18next } from "@translations/oarepo_communities";
import { CommunityItem } from "./CommunityItem";

/* TODO: get actual link for the documentation */

export const GenericCommunityMessage = () => (
  <Trans i18n={i18next} i18nKey="genericCommunityMessage">
    You are not a member of any community. If you choose to proceed, your work
    will be published in the "generic" community. We strongly recommend that you
    join a community to increase the visibility of your work and to cooperate
    with others more easily. You can check the available communities{" "}
    <a
      href="/communities"
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => e.stopPropagation()}
    >
      on our communities page.
    </a>{" "}
    For more details on how to join a community please refer to the instructions
    on{" "}
    <a
      href="/documentation-url"
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => e.stopPropagation()}
    >
      how to join a community.
    </a>{" "}
  </Trans>
);

export const CommunitySelector = ({ fieldPath }) => {
  const { values, setFieldValue } = useFormikContext();
  const lastSelectedCommunity = useRef(null);
  const {
    formConfig: {
      allowed_communities,
      preselected_community,
      generic_community,
    },
  } = useFormConfig();
  const selectedCommunity = getIn(values, "parent.communities.default", "");
  useEffect(() => {
    if (!values.id) {
      if (preselected_community) {
        setFieldValue(fieldPath, preselected_community.id);
        lastSelectedCommunity.current = preselected_community.id;
      } else if (allowed_communities.length === 1) {
        setFieldValue(fieldPath, allowed_communities[0].id);
        lastSelectedCommunity.current = allowed_communities[0].id;
      }
    }
  }, []);

  const handleClick = (id) => {
    setFieldValue(fieldPath, id);
    lastSelectedCommunity.current = id;
  };
  return (
    !values.id && (
      <Modal
        open={!selectedCommunity}
        className="communities community-selection-modal"
      >
        <Modal.Header>{i18next.t("Community selection")}</Modal.Header>
        <Modal.Content>
          {allowed_communities.length > 1 && (
            <div className="communities communities-list-scroll-container">
              <p>
                {i18next.t(
                  "Please select community in which your work will be published:"
                )}
              </p>
              <List selection>
                {allowed_communities.map((c) => (
                  <CommunityItem
                    key={c.id}
                    community={c}
                    handleClick={handleClick}
                    renderLinks={false}
                  />
                ))}
              </List>
            </div>
          )}
          {allowed_communities.length === 0 && (
            <React.Fragment>
              <GenericCommunityMessage />{" "}
              <span>
                {i18next.t(
                  "If you are certain that you wish to proceed with the generic community, please click on it below."
                )}
              </span>
              <List selection>
                <CommunityItem
                  community={generic_community}
                  handleClick={handleClick}
                  renderLinks={false}
                />
              </List>
            </React.Fragment>
          )}
          <Message>
            <Icon name="info circle" className="text size large" />
            <span>{i18next.t("All records must belong to a community.")}</span>
          </Message>
        </Modal.Content>
        <Modal.Actions className="flex">
          {lastSelectedCommunity.current ? (
            <Button
              type="button"
              className="ml-0"
              icon
              labelPosition="left"
              onClick={() =>
                setFieldValue(fieldPath, lastSelectedCommunity.current)
              }
            >
              <Icon name="arrow alternate circle left outline" />
              {i18next.t("Go back")}
            </Button>
          ) : (
            <Button
              type="button"
              className="ml-0"
              icon
              labelPosition="left"
              onClick={() => goBack()}
            >
              <Icon name="arrow alternate circle left outline" />
              {i18next.t("Go back")}
            </Button>
          )}
        </Modal.Actions>
      </Modal>
    )
  );
};

CommunitySelector.propTypes = {
  fieldPath: PropTypes.string,
};

CommunitySelector.defaultProps = {
  fieldPath: "parent.communities.default",
};
